import 'package:flutter/material.dart';
import 'theme.dart';
import 'screens/resource_list_screen.dart';
import 'screens/detail_screens.dart';
import 'screens/create_screens.dart';
import 'screens/attendance_logs_screen.dart';

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
Section _courses() => Section('المواد الدراسية', Icons.menu_book_outlined, () => ResourceListScreen(
      title: 'المواد الدراسية', endpoint: '/api/v1/courses', listKey: 'courses',
      icon: Icons.menu_book_outlined, accent: ShamelColors.gold, searchable: true,
      titleOf: (m) => _s(m, 'title'),
      subtitleOf: (m) => '${_s(m, 'code')} • ${_s(m, 'department')}',
      trailingOf: (m) => '${_s(m, 'hours')}h',
      fab: const _AddFab(CreateCourseScreen()),
    ));

Section _classrooms() => Section('القاعات', Icons.meeting_room_outlined, () => ResourceListScreen(
      title: 'القاعات', endpoint: '/api/v1/classrooms', listKey: 'classrooms',
      icon: Icons.meeting_room_outlined, accent: ShamelColors.primary,
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
      onTap: (ctx, m) => Navigator.push(ctx, MaterialPageRoute(
          builder: (_) => TeacherDetailScreen(teacherId: m['id'] as int))),
    ));

Section _students() => Section('الطلاب', Icons.school_outlined, () => ResourceListScreen(
      title: 'الطلاب', endpoint: '/api/v1/students', listKey: 'students',
      icon: Icons.school_outlined, accent: ShamelColors.roleStudent, searchable: true,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'code')} • ${_s(m, 'department')}',
      onTap: (ctx, m) => Navigator.push(ctx, MaterialPageRoute(
          builder: (_) => StudentDetailScreen(studentId: m['id'] as int))),
    ));

Section _coordStudents() => Section('طلاب الكلية', Icons.school_outlined, () => ResourceListScreen(
      title: 'طلاب الكلية', endpoint: '/api/v1/coordinator/students', listKey: 'students',
      icon: Icons.school_outlined, accent: ShamelColors.roleStudent, searchable: false,
      titleOf: (m) => _s(m, 'name'),
      subtitleOf: (m) => '${_s(m, 'code')} • ${_s(m, 'department')}',
      onTap: (ctx, m) => Navigator.push(ctx, MaterialPageRoute(
          builder: (_) => StudentDetailScreen(studentId: m['id'] as int))),
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
      icon: Icons.event_note_outlined, accent: ShamelColors.warning,
      titleOf: (m) => _s(m, 'course'),
      subtitleOf: (m) => '${_s(m, 'type')} • ${_s(m, 'date')}',
      trailingOf: (m) => _s(m, 'classroom'),
    ));

Section _auditLog() => Section('سجل التدقيق', Icons.history_outlined, () => ResourceListScreen(
      title: 'سجل التدقيق', endpoint: '/api/v1/audit-log', listKey: 'entries',
      icon: Icons.history_outlined, accent: ShamelColors.secondary,
      titleOf: (m) => '${_s(m, 'action')} — ${_s(m, 'target')}',
      subtitleOf: (m) => '${_s(m, 'user')} • ${_s(m, 'timestamp')}',
    ));

Section _tickets() => Section('البلاغات والدعم', Icons.support_agent_outlined, () => ResourceListScreen(
      title: 'البلاغات والدعم', endpoint: '/api/v1/tickets', listKey: 'tickets',
      icon: Icons.support_agent_outlined, accent: ShamelColors.roleTeacher,
      titleOf: (m) => _s(m, 'subject'),
      subtitleOf: (m) => '${_s(m, 'user')} • ${_s(m, 'priority')}',
      trailingOf: (m) => _s(m, 'status'),
      fab: const _AddFab(CreateTicketScreen()),
    ));

Section _search() => Section('البحث الشامل', Icons.search, () => const SearchScreen());
Section _settings() => Section('الإعدادات', Icons.settings_outlined, () => const SettingsScreen());

// ── Role → grouped sections ─────────────────────────────────────────────────
List<SectionGroup> sectionsFor(String role) {
  switch (role) {
    case 'admin':
      return [
        SectionGroup('الإدارة', [_teachers(), _students(), _courses(), _classrooms(), _departments()]),
        SectionGroup('العمليات', [_classroomStatus(), _attendanceLogs(), _gateLogs(), _exams()]),
        SectionGroup('النظام', [_tickets(), _auditLog(), _search(), _settings()]),
      ];
    case 'coordinator':
      return [
        SectionGroup('الإدارة', [_coordStudents(), _teachers(), _courses(), _classrooms()]),
        SectionGroup('العمليات', [_attendanceLogs(), _exams()]),
        SectionGroup('النظام', [_tickets(), _search(), _settings()]),
      ];
    case 'teacher':
      return [
        SectionGroup('التدريس', [_attendanceLogs(), _courses(), _classrooms()]),
        SectionGroup('النظام', [_tickets(), _settings()]),
      ];
    case 'student':
      return [
        SectionGroup('الدراسة', [_courses(), _attendanceLogs()]),
        SectionGroup('النظام', [_tickets(), _settings()]),
      ];
    case 'gate':
      return [
        SectionGroup('البوابة', [_gateLogs(), _classroomStatus()]),
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
        foregroundColor: ShamelColors.primary,
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => target)),
        child: const Icon(Icons.add),
      );
}
