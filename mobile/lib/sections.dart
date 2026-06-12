import 'package:flutter/material.dart';
import 'theme.dart';
import 'screens/resource_list_screen.dart';
import 'screens/detail_screens.dart';
import 'screens/create_screens.dart';
import 'screens/attendance_logs_screen.dart';
import 'screens/schedule_screen.dart';
import 'screens/courses_screen.dart';

/// A navigable section: a label + icon + a builder for its screen.
class Section {
  final String label;
  final IconData icon;
  final Widget Function() build;
  const Section(this.label, this.icon, this.build);
}

class SectionGroup {
  final String title;
  final List<Section> items;
  const SectionGroup(this.title, this.items);
}

String _s(Map m, String k) => '${m[k] ?? ''}';

// ── Reusable section factories ──────────────────────────────────────────────
Section _courses({bool studentMode = false}) => Section(
    'المواد الدراسية', Icons.menu_book_outlined,
    () => CoursesScreen(studentMode: studentMode));

Section _staffCourses() => _courses(studentMode: false);
Section _studentCourses() => _courses(studentMode: true);

Section _classrooms() => Section('القاعات', Icons.meeting_room_outlined, () => ResourceListScreen(
      title: 'القاعات', endpoint: '/api/v1/classrooms', listKey: 'classrooms',
      icon: Icons.meeting_room_outlined, accent: ShamelColors.gold,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'location')} • سعة ${_s(m, 'capacity')}',
      trailingOf: (m) => m['is_busy'] == true ? 'مشغولة' : 'متاحة',
      fab: const _AddFab(CreateClassroomScreen()),
    ));

Section _classroomStatus() => Section('حالة القاعات', Icons.sensors, () => ResourceListScreen(
      title: 'حالة القاعات', endpoint: '/api/v1/classrooms/status', listKey: 'classrooms',
      icon: Icons.sensors, accent: ShamelColors.success,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => _s(m, 'location'),
      trailingOf: (m) => m['is_busy'] == true ? '● مشغولة' : '○ متاحة',
    ));

Section _departments() => Section('الأقسام', Icons.account_tree_outlined, () => ResourceListScreen(
      title: 'الأقسام', endpoint: '/api/v1/departments', listKey: 'departments',
      icon: Icons.account_tree_outlined, accent: ShamelColors.roleCoordinator,
      titleOf: (m) => _s(m, 'name'), subtitleOf: (m) => _s(m, 'college'),
    ));

Section _teachers() => Section('الأساتذة', Icons.groups_outlined, () => ResourceListScreen(
      title: 'الأساتذة', endpoint: '/api/v1/teachers', listKey: 'teachers',
      icon: Icons.groups_outlined, accent: ShamelColors.roleTeacher, searchable: true,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'degree')} • ${_s(m, 'department')}',
      onTap: (ctx, m) => Navigator.push(ctx, ShamelPageRoute(page: TeacherDetailScreen(teacherId: m['id'] as int))),
    ));

Section _students() => Section('الطلاب', Icons.school_outlined, () => ResourceListScreen(
      title: 'الطلاب', endpoint: '/api/v1/students', listKey: 'students',
      icon: Icons.school_outlined, accent: ShamelColors.roleStudent, searchable: true,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'code')} • ${_s(m, 'department')}',
      onTap: (ctx, m) => Navigator.push(ctx, ShamelPageRoute(page: StudentDetailScreen(studentId: m['id'] as int))),
    ));

Section _coordStudents() => Section('طلاب الكلية', Icons.school_outlined, () => ResourceListScreen(
      title: 'طلاب الكلية', endpoint: '/api/v1/coordinator/students', listKey: 'students',
      icon: Icons.school_outlined, accent: ShamelColors.roleStudent, searchable: false,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'code')} • ${_s(m, 'department')}',
      onTap: (ctx, m) => Navigator.push(ctx, ShamelPageRoute(page: StudentDetailScreen(studentId: m['id'] as int))),
    ));

Section _attendanceLogs() => Section('سجلات الحضور', Icons.fact_check_outlined,
    () => const AttendanceLogsScreen());

Section _gateLogs() => Section('سجلات البوابة', Icons.door_sliding_outlined, () => ResourceListScreen(
      title: 'سجلات البوابة', endpoint: '/api/v1/gate-logs', listKey: 'logs',
      icon: Icons.door_sliding_outlined, accent: ShamelColors.roleGate,
      titleOf: (m) => _s(m, 'person'), subtitleOf: (m) => _s(m, 'timestamp'),
      trailingOf: (m) => _s(m, 'status'),
    ));

Section _exams() => Section('الامتحانات', Icons.event_note_outlined, () => ResourceListScreen(
      title: 'الامتحانات', endpoint: '/api/v1/exams', listKey: 'exams',
      icon: Icons.event_note_outlined, accent: ShamelColors.warningText,
      titleOf: (m) => _s(m, 'course'),
      subtitleOf: (m) => '${_s(m, 'type')} • ${_s(m, 'date')}',
      trailingOf: (m) => _s(m, 'classroom'),
    ));

Section _auditLog() => Section('سجل التدقيق', Icons.history_outlined, () => ResourceListScreen(
      title: 'سجل التدقيق', endpoint: '/api/v1/audit-log', listKey: 'entries',
      icon: Icons.history_outlined, accent: ShamelColors.text2Light,
      titleOf: (m) => '${_s(m, 'action')} — ${_s(m, 'target')}',
      subtitleOf: (m) => '${_s(m, 'user')} • ${_s(m, 'timestamp')}',
    ));

Section _tickets() => Section('البلاغات والدعم', Icons.support_agent_outlined, () => ResourceListScreen(
      title: 'البلاغات والدعم', endpoint: '/api/v1/tickets', listKey: 'tickets',
      icon: Icons.support_agent_outlined, accent: ShamelColors.roleTeacher,
      titleOf: (m) => _s(m, 'subject'),
      subtitleOf: (m) => '${_s(m, 'user')} • ${_s(m, 'priority')}',
      trailingOf: (m) => _s(m, 'status'),
      onTap: (ctx, m) => Navigator.push(ctx, ShamelPageRoute(page: TicketDetailScreen(ticketId: m['id'] as int))),
      fab: const _AddFab(CreateTicketScreen()),
    ));

// ScheduleScreen is a bare tab body (no Scaffold). When opened from the drawer
// it needs its own Scaffold+AppBar so it gets a back button.
Section _schedule() => Section('الجدول الدراسي', Icons.calendar_month_outlined,
    () => Scaffold(
          appBar: AppBar(title: const Text('الجدول الدراسي', style: TextStyle(fontWeight: FontWeight.w800))),
          body: const ScheduleScreen(),
        ));

Section _deanEval() => Section('تقييمات العميد', Icons.star_outline, () => ResourceListScreen(
      title: 'تقييمات المقررات', endpoint: '/api/v1/dean-evaluations', listKey: 'evaluations',
      icon: Icons.star_outline, accent: ShamelColors.warningText,
      titleOf: (m) => _s(m, 'course'),
      subtitleOf: (m) => '${_s(m, 'student')} • ${_s(m, 'comment')}',
      trailingOf: (m) => '⭐ ${_s(m, 'rating')}',
    ));

Section _grades() => Section('الدرجات', Icons.grade_outlined, () => ResourceListScreen(
      title: 'الدرجات', endpoint: '/api/v1/grades', listKey: 'grades',
      icon: Icons.grade_outlined, accent: ShamelColors.gold,
      titleOf: (m) => _s(m, 'student'),
      subtitleOf: (m) => _s(m, 'course'),
      trailingOf: (m) => '${_s(m, 'grade')} (${_s(m, 'score')})',
    ));

Section _excuses() => Section('الأعذار الطبية', Icons.medical_services_outlined, () => ResourceListScreen(
      title: 'الأعذار الطبية', endpoint: '/api/v1/excuses', listKey: 'excuses',
      icon: Icons.medical_services_outlined, accent: ShamelColors.error,
      titleOf: (m) => _s(m, 'student'),
      subtitleOf: (m) => _s(m, 'reason'),
      trailingOf: (m) => _s(m, 'status'),
    ));

Section _teacherTimeline() => Section('الجدول الزمني', Icons.timeline_outlined, () => ResourceListScreen(
      title: 'الجدول الزمني', endpoint: '/api/v1/teacher/timeline', listKey: 'sessions',
      icon: Icons.timeline_outlined, accent: ShamelColors.roleTeacher,
      titleOf: (m) => _s(m, 'course'),
      subtitleOf: (m) => _s(m, 'teacher'),
      trailingOf: (m) => m['active'] == true ? '● نشطة' : 'منتهية',
    ));

Section _gateReports() => Section('تقارير البوابة', Icons.assessment_outlined, () => ResourceListScreen(
      title: 'تقارير البوابة', endpoint: '/api/v1/gate-reports', listKey: 'logs',
      icon: Icons.assessment_outlined, accent: ShamelColors.roleGate,
      titleOf: (m) => _s(m, 'person'),
      subtitleOf: (m) => _s(m, 'timestamp'),
      trailingOf: (m) => _s(m, 'status'),
    ));

Section _search() => Section('البحث الشامل', Icons.search, () => const SearchScreen());
Section _settings() => Section('الإعدادات', Icons.settings_outlined, () => const SettingsScreen());

// ── Role → grouped sections ─────────────────────────────────────────────────
List<SectionGroup> sectionsFor(String role) {
  switch (role) {
    case 'admin':
      return [
        SectionGroup('الإدارة', [_teachers(), _students(), _staffCourses(), _classrooms(), _departments(), _schedule()]),
        SectionGroup('العمليات', [_classroomStatus(), _attendanceLogs(), _gateLogs(), _gateReports(), _exams(), _teacherTimeline()]),
        SectionGroup('الأكاديمي', [_grades(), _excuses(), _deanEval()]),
        SectionGroup('النظام', [_tickets(), _auditLog(), _search(), _settings()]),
      ];
    case 'coordinator':
      return [
        SectionGroup('الإدارة', [_coordStudents(), _teachers(), _staffCourses(), _classrooms(), _schedule()]),
        SectionGroup('العمليات', [_attendanceLogs(), _exams()]),
        SectionGroup('الأكاديمي', [_grades(), _excuses()]),
        SectionGroup('النظام', [_tickets(), _search(), _settings()]),
      ];
    case 'teacher':
      return [
        SectionGroup('التدريس', [_teacherTimeline(), _attendanceLogs(), _staffCourses(), _classrooms()]),
        SectionGroup('النظام', [_tickets(), _settings()]),
      ];
    case 'student':
      return [
        SectionGroup('الدراسة', [_studentCourses(), _attendanceLogs(), _grades(), _excuses()]),
        SectionGroup('النظام', [_tickets(), _search(), _settings()]),
      ];
    case 'gate':
      return [
        SectionGroup('البوابة', [_gateLogs(), _gateReports(), _classroomStatus()]),
        SectionGroup('النظام', [_settings()]),
      ];
    default:
      return [SectionGroup('النظام', [_settings()])];
  }
}

/// FloatingActionButton that opens a create screen.
class _AddFab extends StatelessWidget {
  final Widget target;
  const _AddFab(this.target);
  @override
  Widget build(BuildContext context) => FloatingActionButton(
        backgroundColor: ShamelColors.gold,
        foregroundColor: Colors.white,
        onPressed: () => Navigator.push(context, ShamelPageRoute(page: target)),
        child: const Icon(Icons.add),
      );
}
