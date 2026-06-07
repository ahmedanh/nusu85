# Testing-Logs — نظام توثيق اختبارات SHAMEL

نظام لتوثيق كل اختبار ومشكلة تظهر لك أثناء فحص المشروع، يعمل داخل **Obsidian** مع لوحة تتحدث تلقائياً.

## الإعداد (مرة واحدة)
1. افتح هذا الفولدر كـ Vault في أوبسيدين، أو انسخه داخل Vault موجود.
2. فعّل إضافة **Dataview**: `Settings → Community plugins → Browse → Dataview → Install → Enable`.
3. (اختياري) فعّل إضافة **Templates** أو **Templater** لإدراج القالب بسرعة.

## الاستخدام اليومي
- لكل مشكلة جديدة: انسخ `Templates/Bug-Template.md` إلى `Issues/` بترقيم متسلسل (`0002-...`).
- املأ الـ frontmatter: `status`, `severity`, `role`, `platform`, `area`, `date_found`.
- افتح **`🧪 لوحة الاختبارات.md`** لرؤية كل المشاكل مجمّعة ومرتّبة.

## الحقول المهمة
- `status`: open / in-progress / fixed / wont-fix / cannot-reproduce
- `severity`: critical / high / medium / low
- `platform`: web / flutter / api / pwa / face-engine
- `role`: admin / coordinator / teacher / student / gate / api

## الحل بالذكاء الاصطناعي
في أسفل اللوحة استعلام يجمّع المشاكل المفتوحة فقط — مرّره للمساعد ليحلها واحدة واحدة.
