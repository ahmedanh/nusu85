import os
import sys
import cv2
import face_recognition
from datetime import datetime

# 1. إعداد المسارات لضمان عمل المكتبات على جهازك DELL
paths = [
    r'C:\Users\DELL\AppData\Local\Programs\Python\Python312\Lib\site-packages',
    os.path.expanduser("~\\AppData\\Roaming\\Python\\Python312\\site-packages")
]
for p in paths:
    if p not in sys.path:
        sys.path.append(p)

# 2. تحميل الصور من مجلد known_faces
known_face_encodings = []
known_face_names = []
known_faces_dir = "known_faces"

print("⏳ جاري تجهيز كشف الأسماء وتحميل البيانات... انتظر قليلاً")

for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
        # استخراج البصمة الرقمية
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(filename)[0])

print(f"✅ تم تحميل {len(known_face_names)} طلاب بنجاح: {', '.join(known_face_names)}")

# 3. دالة تسجيل الحضور في ملف CSV (إكسل بسيط)
def mark_attendance(name):
    file_path = 'Attendance.csv'
    
    # إذا كان الملف غير موجود، ننشئه ونضع العناوين
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.writelines('Name,Date,Time')

    with open(file_path, 'r+') as f:
        data_list = f.readlines()
        name_list = []
        for line in data_list:
            entry = line.split(',')
            name_list.append(entry[0])
        
        # إذا لم يكن الاسم مسجلاً في القائمة، نقوم بتسجيله الآن
        if name not in name_list:
            now = datetime.now()
            date_string = now.strftime('%Y-%m-%d')
            time_string = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{date_string},{time_string}')
            print(f"⭐ تم تسجيل حضور {name} في ملف الإكسل!")

# 4. تشغيل الكاميرا والمقارنة
video_capture = cv2.VideoCapture(0)
print("🚀 الكاميرا ستفتح الآن.. اضغط 'q' للخروج")

while True:
    ret, frame = video_capture.read()
    if not ret: break

    # تصغير الإطار لتسريع العملية
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # المقارنة مع نسبة تسامح 0.5 لزيادة الدقة
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            # هنا يتم تسجيل الاسم في الملف فور التعرف عليه
            mark_attendance(name)

        # رسم المربع والاسم على الشاشة
        top *= 4; right *= 4; bottom *= 4; left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    cv2.imshow('ACDC Attendance System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

video_capture.release()
cv2.destroyAllWindows()