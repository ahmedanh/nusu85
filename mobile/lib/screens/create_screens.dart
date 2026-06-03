import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';

/// Shared form scaffold with submit handling.
class _FormScaffold extends StatefulWidget {
  final String title;
  final String endpoint;
  final List<_Field> fields;
  const _FormScaffold({required this.title, required this.endpoint, required this.fields});
  @override
  State<_FormScaffold> createState() => _FormScaffoldState();
}

class _Field {
  final String key, label;
  final bool required;
  final TextInputType type;
  final TextEditingController ctrl = TextEditingController();
  _Field(this.key, this.label, {this.required = false, this.type = TextInputType.text});
}

class _FormScaffoldState extends State<_FormScaffold> {
  bool _busy = false;
  String? _error;

  Future<void> _submit() async {
    for (final f in widget.fields) {
      if (f.required && f.ctrl.text.trim().isEmpty) {
        setState(() => _error = 'الحقل "${f.label}" مطلوب');
        return;
      }
    }
    setState(() { _busy = true; _error = null; });
    final body = {for (final f in widget.fields) f.key: f.ctrl.text.trim()};
    try {
      final r = await Api.postJson(widget.endpoint, body);
      if (!mounted) return;
      if (r['ok'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم الحفظ بنجاح'),
            backgroundColor: ShamelColors.success,
            behavior: SnackBarBehavior.floating,
            margin: EdgeInsets.all(12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(10))),
          ));
        Navigator.pop(context, true);
      } else {
        setState(() { _busy = false; _error = (r['message'] ?? 'فشل الحفظ') as String; });
      }
    } catch (e) {
      setState(() { _busy = false; _error = 'تعذّر الاتصال بالخادم'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.w800))),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_error != null)
          Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: ShamelColors.errorContainer, borderRadius: BorderRadius.circular(12)),
            child: Row(children: [
              const Icon(Icons.error_outline, color: ShamelColors.error, size: 18),
              const SizedBox(width: 8),
              Expanded(child: Text(_error!, style: const TextStyle(color: ShamelColors.error, fontWeight: FontWeight.w600))),
            ]),
          ),
        for (final f in widget.fields) ...[
          Align(alignment: Alignment.centerRight, child: Text(
            f.label + (f.required ? ' *' : ''),
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: ShamelColors.secondary))),
          const SizedBox(height: 6),
          TextField(controller: f.ctrl, keyboardType: f.type,
              decoration: InputDecoration(hintText: f.label)),
          const SizedBox(height: 14),
        ],
        const SizedBox(height: 8),
        SizedBox(width: double.infinity, child: ElevatedButton.icon(
          onPressed: _busy ? null : _submit,
          icon: _busy ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.save),
          label: const Text('حفظ'),
        )),
      ]),
    );
  }
}

class CreateCourseScreen extends StatelessWidget {
  const CreateCourseScreen({super.key});
  @override
  Widget build(BuildContext context) => _FormScaffold(
        title: 'إضافة مادة', endpoint: '/api/v1/courses/create',
        fields: [
          _Field('course_code', 'كود المادة', required: true),
          _Field('title', 'عنوان المادة', required: true),
          _Field('credits', 'الساعات المعتمدة', type: TextInputType.number),
          _Field('total_hours', 'إجمالي الساعات', type: TextInputType.number),
          _Field('year_level', 'السنة', type: TextInputType.number),
        ],
      );
}

class CreateClassroomScreen extends StatelessWidget {
  const CreateClassroomScreen({super.key});
  @override
  Widget build(BuildContext context) => _FormScaffold(
        title: 'إضافة قاعة', endpoint: '/api/v1/classrooms/create',
        fields: [
          _Field('name', 'اسم القاعة', required: true),
          _Field('capacity', 'السعة', type: TextInputType.number),
          _Field('location', 'الموقع'),
          _Field('type', 'النوع'),
        ],
      );
}

class CreateTicketScreen extends StatelessWidget {
  const CreateTicketScreen({super.key});
  @override
  Widget build(BuildContext context) => _FormScaffold(
        title: 'رفع بلاغ', endpoint: '/api/v1/tickets/create',
        fields: [
          _Field('subject', 'الموضوع', required: true),
          _Field('body', 'الوصف', required: true),
          _Field('priority', 'الأولوية (low/medium/high)'),
        ],
      );
}
