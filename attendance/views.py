import cv2
import face_recognition
import os
import numpy as np
import time
import csv
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import AIAttendanceLog, Student, Schedule, Course, Teacher, Classroom, StudentFaceEmbedding, Department, Enrollment, TeacherAttendanceLog, TeacherFaceEmbedding, GateEntryLog
from django.core.cache import cache

# --- 1. Global Memory & Settings ---
known_face_encodings = []
known_face_names = []
known_teacher_encodings = []
known_teacher_names = []
last_teacher_seen_time = {}

def load_known_faces():
    global known_face_encodings, known_face_names, known_teacher_encodings, known_teacher_names
    known_face_encodings.clear()
    known_face_names.clear()
    known_teacher_encodings.clear()
    known_teacher_names.clear()
    
    # Load students from DB
    students = StudentFaceEmbedding.objects.select_related('student').all()
    for s_emb in students:
        try:
            arr = np.array([float(x) for x in s_emb.embedding.split(',')])
            known_face_encodings.append(arr)
            known_face_names.append(s_emb.student.name)
        except: pass
            
    # Load teachers from DB
    teachers = TeacherFaceEmbedding.objects.select_related('teacher').all()
    for t_emb in teachers:
        try:
            arr = np.array([float(x) for x in t_emb.face_vector.split(',')])
            known_teacher_encodings.append(arr)
            known_teacher_names.append(t_emb.teacher.name)
        except: pass

# Automatically load on startup
load_known_faces()

def get_current_schedule():
    now = timezone.now() 
    # تأكدي إن الجهاز توقيته صح (السودان حالياً GMT+2)
    current_day = now.strftime('%A') 
    current_time = now.time()
    
    # الـ select_related دي هي اللي بتخلي {{ current_sched.course.name }} يظهر
    return Schedule.objects.select_related('course', 'classroom').filter(
        day_of_week__icontains=current_day,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()
# --- 2. دالة توليد الإطارات (المحرك الذكي) ---
def gen_frames(camera_index=0):
    global last_teacher_seen_time
    camera = cv2.VideoCapture(camera_index)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_counter = 0
    last_log_times = {} 
    last_teacher_log_times = {}

    while True:
        success, frame = camera.read()
        if not success: break
        
        frame_counter += 1
        
        if frame_counter % 6 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            display_frame = cv2.flip(frame, 1)
            width = display_frame.shape[1]
            face_found_in_frame = False
            current_name = "Scanning..."
            current_is_allowed = True

            current_sched = get_current_schedule()

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                
                if True in matches:
                    idx = matches.index(True)
                    current_name = known_face_names[idx]
                    face_found_in_frame = True

                    now_ts = time.time()
                    try:
                        student_obj = Student.objects.filter(name__icontains=current_name).only('id', 'name', 'is_allowed_entry').first()
                        if student_obj:
                            current_is_allowed = getattr(student_obj, 'is_allowed_entry', True)
                            
                            if current_name not in last_log_times or (now_ts - last_log_times[current_name] > 300):
                                GateEntryLog.objects.create(user_name=current_name, user_type='Student', location='Main Gate')
                                if current_is_allowed and current_sched:
                                    AIAttendanceLog.objects.create(
                                        student=student_obj,
                                        schedule=current_sched,
                                        confidence_score=90.0,
                                        status='Present'
                                    )
                                last_log_times[current_name] = now_ts
                    except: pass
                else:
                    teacher_matches = face_recognition.compare_faces(known_teacher_encodings, face_encoding, tolerance=0.5)
                    if True in teacher_matches:
                        idx = teacher_matches.index(True)
                        current_name = known_teacher_names[idx]
                        face_found_in_frame = True
                        now_ts = time.time()
                        last_teacher_seen_time[current_name] = now_ts

                        try:
                            teacher_obj = Teacher.objects.filter(name__icontains=current_name).first()
                            if teacher_obj:
                                current_is_allowed = getattr(teacher_obj, 'is_allowed_entry', True)
                                
                                if current_name not in last_teacher_log_times or (now_ts - last_teacher_log_times[current_name] > 300):
                                    GateEntryLog.objects.create(user_name=current_name, user_type='Teacher', location='Main Gate')
                                    last_teacher_log_times[current_name] = now_ts
                                
                                if current_is_allowed:
                                    active_log = TeacherAttendanceLog.objects.filter(
                                        teacher=teacher_obj,
                                        check_out_time__isnull=True
                                    ).last()
                                    if not active_log:
                                        TeacherAttendanceLog.objects.create(
                                            teacher=teacher_obj,
                                            status='Present'
                                        )
                        except Exception as e:
                            pass

            # Timeout logic for teachers
            now_ts = time.time()
            for t_name, last_seen in list(last_teacher_seen_time.items()):
                if now_ts - last_seen > 300: # 5 minutes timeout
                    try:
                        teacher_obj = Teacher.objects.filter(name__icontains=t_name).first()
                        if teacher_obj:
                            active_log = TeacherAttendanceLog.objects.filter(
                                teacher=teacher_obj,
                                check_out_time__isnull=True
                            ).last()
                            if active_log:
                                active_log.check_out_time = timezone.now()
                                active_log.save()
                    except: pass
                    del last_teacher_seen_time[t_name]

                # Box drawing
                top*=5; right*=5; bottom*=5; left*=5
                m_left, m_right = width-right, width-left
                cv2.rectangle(display_frame, (m_left, top), (m_right, bottom), (34, 197, 94), 2)
                cv2.putText(display_frame, current_name, (m_left+6, bottom-6), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,255,255), 1)

            # Store in Django Cache instead of Global Vars
            cache.set('recognized_status', face_found_in_frame, timeout=5)
            if face_found_in_frame:
                cache.set('last_recognized_info', {
                    'name': current_name,
                    'time': timezone.now().strftime('%I:%M %p'),
                    'course': current_sched.course.title if current_sched else "No Active Session",
                    'is_allowed': current_is_allowed
                }, timeout=5)
            else: 
                cache.set('last_recognized_info', None, timeout=5)

            ret, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        time.sleep(0.01)
# --- 3. الـ Views المكملة ---

def scan_page(request):
    now = timezone.now()
    current_sched = Schedule.objects.filter(
        day_of_week=now.strftime('%A'),
        start_time__lte=now.time(),
        end_time__gte=now.time()
    ).first()
    
    return render(request, 'attendance/scanning/scan.html', {
        'current_sched': current_sched
    })

def video_feed(request):
    try:
        camera_index = int(request.GET.get('camera', 0))
    except ValueError:
        camera_index = 0
    return StreamingHttpResponse(gen_frames(camera_index), content_type='multipart/x-mixed-replace; boundary=frame')

def check_status(request):
    recognized_status = cache.get('recognized_status', False)
    last_recognized_info = cache.get('last_recognized_info', None)
    
    data = {'status': recognized_status}
    if recognized_status and last_recognized_info:
        data.update(last_recognized_info)
        name = last_recognized_info.get('name', '')
        
        data['is_allowed'] = last_recognized_info.get('is_allowed', True)
        data['is_paid'] = True
        data['balance_due'] = 0.0
        data['is_registered'] = True
        data['phone'] = "N/A"
        data['user_id'] = "N/A"
        data['user_type'] = "Unknown"
        
        from .models import Student, Teacher, FinancialStatus
        student = Student.objects.filter(name__icontains=name).first()
        if student:
            data['user_type'] = 'Student'
            data['user_id'] = student.student_code
            data['phone'] = getattr(student, 'phone_number', "N/A") or "N/A"
            data['is_registered'] = getattr(student, 'is_registered', True)
            data['is_allowed'] = getattr(student, 'is_allowed_entry', True)
            fin = FinancialStatus.objects.filter(student=student).first()
            if fin:
                data['is_paid'] = fin.is_paid
                data['balance_due'] = float(fin.balance_due)
        else:
            teacher = Teacher.objects.filter(name__icontains=name).first()
            if teacher:
                data['user_type'] = 'Teacher'
                data['user_id'] = teacher.teacher_id
                data['phone'] = getattr(teacher, 'phone_number', "N/A") or "N/A"
                data['is_allowed'] = getattr(teacher, 'is_allowed_entry', True)
                
    return JsonResponse(data)

def recent_scans(request):
    recent_logs = AIAttendanceLog.objects.select_related('student').order_by('-timestamp')[:5]
    data = []
    for log in recent_logs:
        # بنجيب الوقت بصيغة بسيطة عشان نهرب من مشكلة الـ Naive/Aware
        formatted_time = log.timestamp.strftime('%I:%M %p')
        data.append({
            'name': log.student.name,
            'time': formatted_time
        })
    return JsonResponse(data, safe=False)

def live_stats(request):
    now = timezone.now()
    
    # 1. بنجيب الحصة اللي شغالة حالياً (عشان العنوان فوق)
    current_sched = Schedule.objects.filter(
        day_of_week=now.strftime('%A'), 
        start_time__lte=now.time(), 
        end_time__gte=now.time()
    ).first()

    # 2. بنجيب آخر شخص تم رصده في "آخر 5 ثواني" فقط (عشان المربع التحت)
    # لو مافيش زول قدام الكاميرا، latest_active_log حتكون فاضية
    latest_active_log = AIAttendanceLog.objects.filter(
        timestamp__gte=now - timedelta(seconds=5)
    ).order_by('-timestamp').first()

    data = {
        # إحصائيات عامة
        "total_attendance": AIAttendanceLog.objects.filter(timestamp__date=now.date()).count(),
        "system_status": "Active",
        
        # بيانات العنوان (Session | Room)
        "current_session": current_sched.course.title if current_sched else "No Active Session",
        "room_name": current_sched.classroom.name if current_sched else "N/A",
        
        # بيانات المربع التحت (الرادار اللحظي)
        "active_scanner_name": latest_active_log.student.name if latest_active_log else "Scanning..."
    }
    return JsonResponse(data)

@login_required
def attendance_logs(request):
    # جلب كل سجلات الحضور وترتيبها من الأحدث للأقدم
    logs = AIAttendanceLog.objects.select_related('student', 'schedule').all().order_by('-timestamp')
    return render(request, 'attendance/attendance_logs.html', {'logs': logs})

@staff_member_required
def admin_control_panel(request):
    total_students_count = Student.objects.count()
    active_teachers_count = Teacher.objects.count()
    teachers_list = Teacher.objects.all().order_by('teacher_id')
    classrooms = Classroom.objects.all()
    
    trained_students = StudentFaceEmbedding.objects.count()
    if total_students_count > 0:
        training_progress = int((trained_students / total_students_count) * 100)
    else:
        training_progress = 0
        
    context = {
        'classrooms': classrooms,
        'total_students': total_students_count,
        'active_faculty': active_teachers_count,
        'teachers': teachers_list,
        'training_progress': training_progress,
        'batch_number': total_students_count + 100,
    }
    return render(request, 'attendance/admin_control_panel.html', context)

@staff_member_required
def faculty_management(request):
    # سحب كل المعلمين من جدول Teacher
    teachers = Teacher.objects.all()
    # سحب كل الأقسام عشان الـ Dropdown يشتغل ديناميكياً
    departments = Department.objects.all()
    
    context = {
        'teachers': teachers,
        'departments': departments,
    }
    return render(request, 'attendance/faculty_management.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user:
            login(request, user)
            from .models import Coordinator, Teacher, Student
            if user.is_superuser or user.is_staff:
                return redirect('admin_panel')
            elif Coordinator.objects.filter(auth_user=user).exists():
                return redirect('coordinator_dashboard')
            elif Teacher.objects.filter(auth_user=user).exists():
                return redirect('professor_dashboard')
            elif Student.objects.filter(auth_user=user).exists():
                return redirect('student_dashboard')
            elif user.groups.filter(name='GATE_STAFF').exists():
                return redirect('gate_page')
            else:
                return redirect('scan_page')
        
        # لو البيانات غلط
        return render(request, 'attendance/university_login.html', {'error': 'Invalid login'})
        
    return render(request, 'attendance/university_login.html')

@login_required
def attendance_success(request):
    try:
        last_log = AIAttendanceLog.objects.latest('timestamp')
        return render(request, 'attendance/attendance_success.html', {'student': last_log.student})
    except AIAttendanceLog.DoesNotExist:
        return redirect('scan_page')

@login_required
def attendance_error(request):
    try:
        # هنا ممكن نجيب آخر خطأ حصل لو حابة تعرضي تفاصيل، 
        # أو ببساطة نوجه المستخدم لصفحة الخطأ المصممة عندك
        return render(request, 'attendance/attendance_error.html')
    except Exception as e:
        # لو حتى صفحة الخطأ فيها مشكلة، رجعيه لصفحة الكاميرا
        return redirect('scan_page')

@login_required
def professor_dashboard(request):
    # استخدام now() مباشرة، الدجانقو حيعرف يتعامل معاها
    now_dt = timezone.now() 
    current_time = now_dt.time()
    current_day = now_dt.strftime('%A')

    current_teacher = get_object_or_404(Teacher, auth_user=request.user)

    # جلب الحصة اللي شغالة "حسا" بناءً على اليوم والوقت
    current_session = Schedule.objects.filter(
        teacher=current_teacher,
        day_of_week=current_day,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()
    
    if current_session:
        # حضور اليوم فقط لهذه الحصة
        present_students = AIAttendanceLog.objects.filter(
            schedule=current_session, 
            status='Present',
            timestamp__date=now_dt.date() 
        )
        
        present_ids = present_students.values_list('student_id', flat=True)
        
        # جلب الطلاب المسجلين في المادة دي فقط (عشان الـ total_count يبقى صح)
        enrolled_students = Enrollment.objects.filter(course=current_session.course)
        total_count = enrolled_students.count()
        
        # الغائبين هم المسجلين في المادة ناقص اللي حضروا
        absent_students = Student.objects.filter(
            id__in=enrolled_students.values_list('student_id', flat=True)
        ).exclude(id__in=present_ids)
        
        next_session = Schedule.objects.filter(
            teacher=current_teacher,
            day_of_week=current_day,
            start_time__gt=current_time
        ).order_by('start_time').first()
        
        room_name = current_session.classroom.name
    else:
        present_students = []
        absent_students = []
        next_session = None
        room_name = "N/A"
        total_count = 0

    context = {
        'current_session': current_session, # لازم تمرري ده عشان الـ Template يظهر البيانات
        'present_count': len(present_students),
        'total_count': total_count,
        'present_students': present_students,
        'absent_students': absent_students,
        'room_number': room_name,
        'next_session': next_session,
    }
    return render(request, 'attendance/professor_dashboard.html', context)

@login_required
def stop_session(request, session_id):
    if request.method == 'POST':
        from .models import LectureSession
        session = get_object_or_404(LectureSession, id=session_id)
        session.is_active = False
        session.actual_end_time = timezone.now()
        if session.actual_start_time:
            delta = session.actual_end_time - session.actual_start_time
            session.duration_minutes = int(delta.total_seconds() / 60)
        session.save(update_fields=['is_active', 'actual_end_time', 'duration_minutes'])
        
        if session.schedule and session.schedule.classroom:
            classroom = session.schedule.classroom
            classroom.is_busy = False
            classroom.is_occupied = False
            classroom.save(update_fields=['is_busy', 'is_occupied'])
    
    # بعد ما يقفل، يرجعه للـ Dashboard أو صفحة تانية
    return redirect('professor_dashboard')
    
@login_required
def global_search(request):
    query = request.GET.get('q', '')
    results = []
    
    if len(query) > 1:
        # البحث في الطلاب
        students = Student.objects.filter(name__icontains=query)[:3]
        for s in students:
            results.append({
                'id': s.id,
                'title': s.name,
                'sub': 'Student',
                'icon': 'person'
            })
            
        # البحث في الأساتذة
        teachers = Teacher.objects.filter(name__icontains=query)[:3]
        for t in teachers:
            results.append({
                'id': t.id,
                'title': t.name,
                'sub': 'Faculty',
                'icon': 'school'
            })
            
    return JsonResponse({'results': results})

@staff_member_required
def settings_view(request):
    # الدالة دي وظيفتها بس تعرض الصفحة
    return render(request, 'attendance/settings.html')

@staff_member_required
def update_settings(request):
    if request.method == 'POST':
        # 1. استلام البيانات
        admin_name = request.POST.get('name')
        admin_email = request.POST.get('email')
        # الـ Checkbox في HTML بيبعت 'on' لو متعلم عليه، أو None لو لا
        face_tracking = request.POST.get('face_tracking') == 'on' 
        auto_sync = request.POST.get('auto_sync') == 'on'

        # 2. منطق الحفظ (Logic)
        # هنا بنحدث بيانات المستخدم الحالي (اللي هو إنتِ كـ Admin)
        user = request.user
        if admin_name:
            # بنقسم الاسم لـ First و Last عشان Django User Model
            names = admin_name.split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1: user.last_name = names[1]
        
        user.email = admin_email
        user.save()

        # 3. رسالة نجاح احترافية
        messages.success(request, "Settings updated successfully! ✅")
        
        # 4. التوجيه (Redirect)
    return redirect('settings_page') 

@staff_member_required
def get_chancellor_stats(request):
    # 1. عدد الطلاب الفعلي المسجلين في السيستم
    total_students = Student.objects.count()
    
    # 2. حساب الدقة الحقيقية (بناخد متوسط الـ accuracy من سجلات الحضور)
    # بيفترض إن عندك حقل اسمه confidence أو accuracy في جدول الـ Attendance
    avg_accuracy = AIAttendanceLog.objects.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
    
    # 3. حالة القاعات (كم قاعة مشغول حالياً)
    occupied_rooms = Classroom.objects.filter(is_occupied=True).count()
    total_rooms = Classroom.objects.count()
    
    # 4. نسبة تدريب الـ AI (ممكن تحسبيها بنسبة الطلاب اللي عندهم بصمة وجه جاهزة)
    trained_students = Student.objects.filter(is_trained=True).count()
    if total_students > 0:
        training_progress = int((trained_students / total_students) * 100)
    else:
        training_progress = 0

    data = {
        'total_students': total_students,
        'global_accuracy': round(avg_accuracy, 1), # بيطلع ليك مثلاً 98.2
        'training_progress': training_progress,   # نسبة حقيقية للطلاب الجاهزين
        'occupied_rooms': occupied_rooms,
        'total_rooms': total_rooms,
    }
    return JsonResponse(data)


@staff_member_required
def reports_view(request):
    # 1. حساب متوسط الحضور الكلي (Real-time)
    total_records = AIAttendanceLog.objects.count()
    present_records = AIAttendanceLog.objects.filter(status='Present').count()
    avg_attendance = (present_records / total_records * 100) if total_records > 0 else 0

    # 2. إجمالي الجلسات (Sessions)
    total_sessions = AIAttendanceLog.objects.values('schedule_id').distinct().count()

    # 3. دقة الـ AI (بناءً على الـ Confidence Score)
    ai_accuracy = AIAttendanceLog.objects.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 94.2

    # 4. تجهيز بيانات الرسم البياني (Weekly Trends)
    # ملاحظة: Django week_day بيبدأ بـ 1 (الأحد) وينتهي بـ 7 (السبت)
    days_map = {1: 'Sun', 2: 'Mon', 3: 'Tue', 4: 'Wed', 5: 'Thu', 6: 'Fri'}
    weekly_attendance = {day: 0 for day in days_map.values()}
    
    for num, label in days_map.items():
        day_logs = AIAttendanceLog.objects.filter(timestamp__week_day=num)
        day_total = day_logs.count()
        if day_total > 0:
            day_present = day_logs.filter(status='Present').count()
            weekly_attendance[label] = (day_present / day_total * 100)

    # 5. أفضل الأقسام حضوراً (Leaderboard) - النسخة المعدلة لصورك
    # بنجيب الأقسام ونحسب الحضور لكل واحد
    top_departments_list = []
    depts = Department.objects.all()

    for dept in depts:
        # بنحسب الطلاب التابعين للقسم ده
        dept_students = Student.objects.filter(department=dept)
        total_dept_students = dept_students.count()
        
        if total_dept_students > 0:
            # بنحسب كم طالب من القسم ده عنده سجل "حاضر"
            present_in_dept = AIAttendanceLog.objects.filter(
                student__department=dept, 
                status='Present'
            ).count()
            
            rate = (present_in_dept / (total_dept_students * 10) * 100) # افتراض 10 محاضرات كمتوسط
            # لو الحسبة معقدة، ممكن تخليها: (present_in_dept / AIAttendanceLog.objects.filter(student__department=dept).count() * 100)
            
            top_departments_list.append({
                'name': dept.name,
                'rate': round(min(rate, 100), 1) # عشان النسبة ما تزيد عن 100
            })

    # ترتيب الأقسام تنازلياً
    top_departments_list = sorted(top_departments_list, key=lambda x: x['rate'], reverse=True)[:3]

    context = {
        'avg_attendance': round(avg_attendance, 1),
        'growth': 5.4,
        'total_sessions': total_sessions,
        'ai_accuracy': round(ai_accuracy, 1),
        'weekly_data': weekly_attendance,
        'top_departments': top_departments_list,
    }

    return render(request, 'attendance/reports.html', context)
    
@staff_member_required
def export_teachers_csv(request):
    # إعداد ملف الـ CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="faculty_data.csv"'

    writer = csv.writer(response)
    # كتابة رؤوس الأعمدة
    writer.writerow(['ID', 'Name', 'Major', 'Degree'])

    # سحب البيانات من قاعدة البيانات
    teachers = Teacher.objects.all()
    for teacher in teachers:
        writer.writerow([teacher.teacher_id, teacher.name, teacher.major, teacher.academic_degree])

    return response

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_face(request, user_type, user_id):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            
            # Generate encoding directly from memory
            image = face_recognition.load_image_file(image_file)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                encoding_str = ','.join(str(x) for x in encodings[0])
                
                if user_type == 'teacher':
                    teacher = get_object_or_404(Teacher, pk=user_id)
                    TeacherFaceEmbedding.objects.update_or_create(
                        teacher=teacher,
                        defaults={'face_vector': encoding_str}
                    )
                    teacher.is_allowed_entry = True
                    teacher.save(update_fields=['is_allowed_entry'])
                elif user_type == 'student':
                    student = get_object_or_404(Student, pk=user_id)
                    StudentFaceEmbedding.objects.update_or_create(
                        student=student,
                        defaults={'embedding': encoding_str}
                    )
                    student.is_trained = True
                    student.save(update_fields=['is_trained'])
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid user type'}, status=400)
                    
                # Reload memory
                load_known_faces()
                
                return JsonResponse({'status': 'success', 'message': 'Face uploaded and trained successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No face detected in the uploaded image'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def gate_page(request):
    return render(request, 'attendance/gate.html')

@staff_member_required
def toggle_user_access(request, user_type, user_id):
    if user_type == 'student':
        obj = get_object_or_404(Student, id=user_id)
    elif user_type == 'teacher':
        obj = get_object_or_404(Teacher, teacher_id=user_id)
    else:
        return redirect('admin_panel')
        
    obj.is_allowed_entry = not obj.is_allowed_entry
    obj.save(update_fields=['is_allowed_entry'])
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel'))

@login_required
def schedule_view(request):
    schedules = Schedule.objects.select_related('course', 'classroom', 'teacher').all().order_by('start_time')
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    grouped_schedules = {day: [] for day in days}
    
    for s in schedules:
        if s.day_of_week in grouped_schedules:
            grouped_schedules[s.day_of_week].append(s)
            
    grouped_schedules = {k: v for k, v in grouped_schedules.items() if v}
    
    return render(request, 'attendance/schedule.html', {'grouped_schedules': grouped_schedules})

@staff_member_required
def student_attendance_report(request):
    logs = AIAttendanceLog.objects.all()
    
    course_id = request.GET.get('course_id')
    student_id = request.GET.get('student_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if course_id:
        logs = logs.filter(schedule__course_id=course_id)
    if student_id:
        logs = logs.filter(student_id=student_id)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
        
    logs = logs.select_related('student', 'schedule__course')
    
    return render(request, 'attendance/reports/student_report.html', {'logs': logs})

@staff_member_required
def export_student_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_attendance.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Course', 'Attendance Date', 'Status'])
    
    logs = AIAttendanceLog.objects.all()
    
    course_id = request.GET.get('course_id')
    student_id = request.GET.get('student_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if course_id:
        logs = logs.filter(schedule__course_id=course_id)
    if student_id:
        logs = logs.filter(student_id=student_id)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
        
    logs = logs.select_related('student', 'schedule__course')
    
    for log in logs:
        writer.writerow([
            log.student.name, 
            log.schedule.course.title if log.schedule and log.schedule.course else 'N/A', 
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
            log.status
        ])
        
    return response

@staff_member_required
def teacher_attendance_report(request):
    logs = TeacherAttendanceLog.objects.all()
    
    teacher_id = request.GET.get('teacher_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if teacher_id:
        logs = logs.filter(teacher__teacher_id=teacher_id)
    if date_from:
        logs = logs.filter(check_in_time__date__gte=date_from)
    if date_to:
        logs = logs.filter(check_in_time__date__lte=date_to)
        
    logs = logs.select_related('teacher')
    
    for log in logs:
        if log.check_out_time:
            delta = log.check_out_time - log.check_in_time
            log.duration_minutes = int(delta.total_seconds() / 60)
        else:
            log.duration_minutes = 'N/A'
            
    return render(request, 'attendance/reports/teacher_report.html', {'logs': logs})

@staff_member_required
def export_teacher_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teacher_attendance.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow(['Teacher Name', 'Date', 'Check-in Time', 'Check-out Time', 'Duration (Minutes)'])
    
    logs = TeacherAttendanceLog.objects.all()
    
    teacher_id = request.GET.get('teacher_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if teacher_id:
        logs = logs.filter(teacher__teacher_id=teacher_id)
    if date_from:
        logs = logs.filter(check_in_time__date__gte=date_from)
    if date_to:
        logs = logs.filter(check_in_time__date__lte=date_to)
        
    logs = logs.select_related('teacher')
    
    for log in logs:
        duration = 'N/A'
        if log.check_out_time:
            delta = log.check_out_time - log.check_in_time
            duration = int(delta.total_seconds() / 60)
            
        writer.writerow([
            log.teacher.name,
            log.check_in_time.strftime('%Y-%m-%d'),
            log.check_in_time.strftime('%H:%M:%S'),
            log.check_out_time.strftime('%H:%M:%S') if log.check_out_time else 'N/A',
            duration
        ])
        
    return response

@login_required
def export_my_courses_csv(request):
    current_teacher = get_object_or_404(Teacher, auth_user=request.user)
    schedules = Schedule.objects.filter(teacher=current_teacher).select_related('course')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_courses.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow(['Course Name', 'Completed Lectures', 'Total Scheduled Lectures', 'First Lecture Date', 'Last Lecture Date'])
    
    for sched in schedules:
        from .models import LectureSession
        sessions = LectureSession.objects.filter(schedule=sched)
        completed = sessions.filter(is_active=False).count()
        total_lectures = 15 # Default/Mock or query if you have it in course
        
        first_date = sessions.order_by('date').first()
        last_date = sessions.order_by('date').last()
        
        writer.writerow([
            sched.course.title if sched.course else 'N/A',
            completed,
            total_lectures,
            first_date.date if first_date else 'N/A',
            last_date.date if last_date else 'N/A'
        ])
        
    return response

@login_required
def student_dashboard(request):
    from .models import Student, Enrollment, Schedule, AIAttendanceLog
    student = get_object_or_404(Student, auth_user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    # Calculate attendance %
    total_lectures = 0
    attended_lectures = 0
    for e in enrollments:
        total = Schedule.objects.filter(course=e.course).count() * 10  # Assuming 10 weeks
        attended = AIAttendanceLog.objects.filter(student=student, schedule__course=e.course, status='Present').count()
        total_lectures += total
        attended_lectures += attended
        
    attendance_percentage = (attended_lectures / total_lectures * 100) if total_lectures > 0 else 0
    
    # Weekly schedule
    schedules = Schedule.objects.filter(course__in=enrollments.values_list('course_id', flat=True)).order_by('start_time')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_schedule = {day: [] for day in days}
    for s in schedules:
        if s.day_of_week in weekly_schedule:
            weekly_schedule[s.day_of_week].append(s)
            
    weekly_schedule = {k: v for k, v in weekly_schedule.items() if v}
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'attendance_percentage': round(attendance_percentage, 1),
        'weekly_schedule': weekly_schedule
    }
    return render(request, 'attendance/student_dashboard.html', context)

@login_required
def student_profile(request):
    from .models import Student
    student = get_object_or_404(Student, auth_user=request.user)
    return render(request, 'attendance/student_profile.html', {'student': student})

@login_required
def student_courses(request):
    from .models import Student, Enrollment
    student = get_object_or_404(Student, auth_user=request.user)
    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'classroom')
    return render(request, 'attendance/student_courses.html', {'enrollments': enrollments})

@login_required
def student_support(request):
    from .models import SupportTicket
    if request.method == 'POST':
        subject = request.POST.get('subject')
        request_type = request.POST.get('request_type')
        description = request.POST.get('description')
        SupportTicket.objects.create(
            requester=request.user,
            subject=subject,
            request_type=request_type,
            description=description
        )
        messages.success(request, 'Ticket submitted successfully.')
        return redirect('student_support')
        
    tickets = SupportTicket.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'attendance/student_support.html', {'tickets': tickets})

@login_required
def open_session(request, schedule_id):
    from .models import Teacher, Schedule, ClassroomPermission, LectureSession
    teacher = get_object_or_404(Teacher, auth_user=request.user)
    schedule = get_object_or_404(Schedule, id=schedule_id, teacher=teacher)
    
    # Check ClassroomPermission
    now_time = timezone.now().time()
    permission = ClassroomPermission.objects.filter(
        teacher=teacher,
        classroom=schedule.classroom,
        allowed_from__lte=now_time,
        allowed_until__gte=now_time
    ).first()
    
    if not permission:
        messages.error(request, 'You do not have permission to open a session in this classroom at this time.')
        return redirect('professor_dashboard')
        
    # Create LectureSession
    timer_duration = int(request.POST.get('timer_duration', 60))
    session = LectureSession.objects.create(
        schedule=schedule,
        is_active=True,
        timer_duration=timer_duration
    )
    
    # Mark classroom busy
    schedule.classroom.is_busy = True
    schedule.classroom.is_occupied = True
    schedule.classroom.save(update_fields=['is_busy', 'is_occupied'])
    
    messages.success(request, 'Session started successfully.')
    return redirect('professor_dashboard')

@login_required
def teacher_timeline(request):
    from .models import Teacher, LectureSession
    teacher = get_object_or_404(Teacher, auth_user=request.user)
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        topic = request.POST.get('topic')
        summary = request.POST.get('summary')
        
        session = get_object_or_404(LectureSession, id=session_id, schedule__teacher=teacher)
        session.topic = topic
        session.summary = summary
        session.save(update_fields=['topic', 'summary'])
        messages.success(request, 'Session details updated.')
        return redirect('teacher_timeline')
        
    sessions = LectureSession.objects.filter(schedule__teacher=teacher).select_related('schedule__course').order_by('-actual_start_time')
    return render(request, 'attendance/teacher_timeline.html', {'sessions': sessions})

@login_required
def teacher_attendance_records(request):
    from .models import Teacher, Course, AIAttendanceLog
    teacher = get_object_or_404(Teacher, auth_user=request.user)
    courses = Course.objects.filter(schedule__teacher=teacher).distinct()
    
    logs = AIAttendanceLog.objects.filter(schedule__teacher=teacher).select_related('student', 'schedule__course')
    
    course_id = request.GET.get('course_id')
    date_from = request.GET.get('date_from')
    
    if course_id:
        logs = logs.filter(schedule__course_id=course_id)
    if date_from:
        logs = logs.filter(timestamp__date=date_from)
        
    logs = logs.order_by('-timestamp')
    return render(request, 'attendance/teacher_attendance_records.html', {'logs': logs, 'courses': courses})

# --- Phase 4: Coordinator Views ---

@login_required
def coordinator_dashboard(request):
    from .models import Coordinator, Student, Teacher, AIAttendanceLog
    from django.db.models import Count
    
    coordinator = get_object_or_404(Coordinator, auth_user=request.user)
    
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.filter(college=coordinator.college).count()
    
    total_logs = AIAttendanceLog.objects.filter(schedule__course__college=coordinator.college).count()
    present_logs = AIAttendanceLog.objects.filter(schedule__course__college=coordinator.college, status='Present').count()
    
    college_attendance_pct = (present_logs / total_logs * 100) if total_logs > 0 else 0
    
    # Low-attendance warnings
    students_warnings = Student.objects.annotate(
        total=Count('aiattendancelog'),
        presents=Count('aiattendancelog', filter=Q(aiattendancelog__status='Present'))
    ).filter(total__gt=0)
    
    low_attendance_students = []
    for s in students_warnings:
        rate = (s.presents / s.total) * 100
        if rate < 50:
            low_attendance_students.append({'student': s, 'rate': round(rate, 1)})
            
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'college_attendance_pct': round(college_attendance_pct, 1),
        'low_attendance_students': low_attendance_students,
    }
    return render(request, 'attendance/coordinator_dashboard.html', context)

@login_required
def coordinator_students(request):
    from .models import Student, FinancialStatus
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        student = get_object_or_404(Student, id=student_id)
        
        if action == 'toggle_registered':
            student.is_registered = not student.is_registered
            student.save(update_fields=['is_registered'])
            messages.success(request, f"Registration toggled for {student.name}")
        return redirect('coordinator_students')
        
    students = Student.objects.select_related('financialstatus').all()
    return render(request, 'attendance/coordinator_students.html', {'students': students})

@login_required
def coordinator_faculty(request):
    from .models import Teacher, Schedule, LectureSession
    teachers = Teacher.objects.all()
    return render(request, 'attendance/coordinator_faculty.html', {'teachers': teachers})

@login_required
def coordinator_course_assignment(request):
    from .models import Teacher, Course, Classroom, Schedule
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        course_id = request.POST.get('course_id')
        classroom_id = request.POST.get('classroom_id')
        batch = request.POST.get('batch')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # Validation: check teacher or classroom double booking
        conflict_teacher = Schedule.objects.filter(
            teacher_id=teacher_id, day_of_week=day_of_week, 
            start_time__lt=end_time, end_time__gt=start_time
        ).exists()
        
        conflict_classroom = Schedule.objects.filter(
            classroom_id=classroom_id, day_of_week=day_of_week, 
            start_time__lt=end_time, end_time__gt=start_time
        ).exists()
        
        if conflict_teacher:
            messages.error(request, 'Double booking error: Teacher is already assigned at this time.')
        elif conflict_classroom:
            messages.error(request, 'Double booking error: Classroom is already occupied at this time.')
        else:
            Schedule.objects.create(
                teacher_id=teacher_id,
                course_id=course_id,
                classroom_id=classroom_id,
                batch=batch,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Course assigned successfully!')
        return redirect('coordinator_course_assignment')
        
    teachers = Teacher.objects.all()
    courses = Course.objects.all()
    classrooms = Classroom.objects.all()
    return render(request, 'attendance/coordinator_course_assignment.html', {
        'teachers': teachers, 'courses': courses, 'classrooms': classrooms
    })

@login_required
def coordinator_register_user(request):
    from django.contrib.auth.models import User as AuthUser
    from django.contrib.auth.hashers import make_password
    from .models import Student, Teacher, FinancialStatus
    from django.contrib.auth.models import Group
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if AuthUser.objects.filter(username=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('coordinator_register_user')
            
        auth_user = AuthUser.objects.create(
            username=email,
            email=email,
            password=make_password(password)
        )
        
        if user_type == 'student':
            student_code = request.POST.get('code')
            student = Student.objects.create(
                auth_user=auth_user,
                name=name,
                student_code=student_code,
                university_email=email,
                phone_number=phone
            )
            FinancialStatus.objects.create(
                student=student,
                is_paid=False,
                balance_due=0.0
            )
            messages.success(request, 'Student created successfully. User can now login and configure Face ID.')
        elif user_type == 'teacher':
            teacher = Teacher.objects.create(
                auth_user=auth_user,
                name=name,
                university_email=email,
                phone_number=phone
            )
            messages.success(request, 'Teacher created successfully. User can now login and configure Face ID.')
            
        return redirect('coordinator_register_user')
        
    return render(request, 'attendance/coordinator_register_user.html')