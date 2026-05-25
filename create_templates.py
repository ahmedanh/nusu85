import os

base_dir = r'c:\Users\ahmed\Downloads\ACDC_FINAL-main\ACDC_FINAL-main\attendance\templates\attendance'

missing_templates = [
    'coordinator_dashboard.html',
    'student_dashboard.html',
    'coordinator_students.html',
    'coordinator_faculty.html',
    'coordinator_course_assignment.html',
    'coordinator_register_user.html',
    'student_profile.html',
    'student_courses.html',
    'student_support.html',
    'teacher_timeline.html',
    'teacher_attendance_records.html'
]

for template in missing_templates:
    path = os.path.join(base_dir, template)
    content = "{% extends 'attendance/base.html' %}\n{% block content %}\n<h1>" + template + "</h1>\n{% endblock %}"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
