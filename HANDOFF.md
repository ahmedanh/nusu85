# SHAMEL — Session Handoff

> ابدأ محادثة جديدة وأعطها هذا الملف. يلخّص كل ما تم والنهج المتبع.

---

## 1. القاعدة الذهبية: قاعدتا بيانات منفصلتان ⚠️

النظام يكتشف PostgreSQL VPS تلقائياً عند الإقلاع:
- **متصل بالـ VPS** → PostgreSQL (فيه 9889 طالب — بيانات قديمة)
- **VPS غير متاح / `USE_LOCAL_DB=true`** → `db_local.sqlite3` (فيه بيانات الـ seed)

**كل السكربتات (`seed_demo_data.py`, `e2e_test.py`, `autotest*.py`) تفرض `USE_LOCAL_DB=true`** → تكتب في SQLite.

### ⛔ الخطأ الذي وقع: 
الـ seed كتب في SQLite، لكن `runserver` بدون env اتصل بـ PostgreSQL → البيانات "اختفت".

### ✅ القاعدة:
**شغّل الـ server دائماً بـ `USE_LOCAL_DB=true` ليطابق السكربتات:**
```powershell
$env:USE_LOCAL_DB = "true"
python manage.py runserver 0.0.0.0:8000 --noreload
```

---

## 2. أوامر التشغيل

```powershell
# Django (لازم USE_LOCAL_DB=true ليرى بيانات الـ seed)
$env:USE_LOCAL_DB = "true"
python3.13 manage.py runserver 0.0.0.0:8000 --noreload

# Login سريع لأي دور (DEBUG فقط)
# http://127.0.0.1:8000/demo-login/?role=admin   (أو coordinator/teacher/student)

# Seed بيانات واقعية (كلية حاسوب، 24 طالب، 2349 سجل حضور، 67 رفض بوابة، أعذار، مقاعد امتحان)
python -X utf8 seed_demo_data.py

# اختبارات
python e2e_test.py        # كل المسارات لكل دور
python autotest2.py       # عميق: PDF/CSV/Excel + API

# Flutter (المسار الكامل لازم — flutter مش في PATH)
cd mobile
& "C:\develop\flutter\bin\flutter.bat" analyze --no-pub
& "C:\develop\flutter\bin\flutter.bat" build apk --release
# adb في: C:\Users\ahmed\AppData\Local\Android\Sdk\platform-tools\adb.exe
```

---

## 3. فخّ الـ Templates المزدوجة ⚠️

كل template موجود في **نسختين**:
- `attendance/templates/attendance/X.html`        ← APP_DIRS path
- `attendance/templates/templates/attendance/X.html` ← DIRS path (settings.TEMPLATES DIRS)

**الـ DIRS path له الأولوية — هو الذي يُخدَّم فعلاً.** عند تعديل أي template **عدّل النسختين** أو تحقق أيهما يُخدَّم:
```python
# للتأكد أيهما يُحمَّل:
from django.template.loader import get_template
print(get_template('attendance/admin_panel.html').origin.name)
```

---

## 4. درس CSS مهم (الألوان)

**لا تعتمد على Tailwind CDN classes للألوان الحرجة.** `base.html` فيه override layer ضخم يصارع الـ classes (مثلاً `html:not(.dark) .text-white { color:#0B2545 }` يحوّل أي `text-white` لداكن في light mode، و `bg-primary` = ذهبي `#C9A227` لا أزرق).

**الحل المضمون: inline `style="color:#..."`** — لا يتصارع مع أي شيء. والـ base.html يحوّل تلقائياً في dark mode:
```css
.dark [style*="color:#0B2545"] { color:#F1F5F9 !important; }
.dark [style*="background:#FFFFFF"] { background:#1E293B !important; }
.dark [style*="color:#64748B"] { color:#94A3B8 !important; }
```

---

## 5. درس Material Symbols (الأيقونات)

الخط يستخدم **ligatures** (نص ASCII مثل `face`, `school` → أيقونة). 
- ❌ **لا تضف `unicode-range`** لـ `@font-face` — يكسر كل الأيقونات (ASCII لا يُطبَّق عليه الخط).
- ✅ الصحيح فقط: `direction: ltr !important` على `.material-symbols-outlined` (يمنع RTL من قلب ترتيب الـ ligature).
- الخط محلي: `attendance/static/fonts/material-symbols.ttf` + preload في base.html.

---

## 6. النهج المتبع للترجمة (i18n)

JS-based: `<span data-en="Text" data-ar="نص">Text</span>` + سكربت في base.html يبدّل حسب `localStorage.acdc_lang`. صفحة الـ login مستقلة (لا تـ extend base.html) فلها سكربت i18n خاص بداخلها.

---

## 7. ما تم إنجازه (commits على فرع `fix/ui-bugs-financial-cleanup`)

PR: https://github.com/ahmedanh/nusu85/pull/1

- Pagination + sticky column + skeleton loaders + multi-step wizard (web)
- Dark-mode contrast site-wide + 9 PDF-audit fixes (mobile cards, charts, RTL, empty states)
- N+1 query fixes، PWA banner suppressed، Flutter keyboard overlap
- **فصل الأدوار**: Admin (بنية تحتية عالمية) ≠ Coordinator (أكاديمي مقيّد بالكلية)
- **إزالة toggle دخول الأستاذ** (الأستاذ موظف، دخوله مضمون — فقط الطلاب لهم `is_allowed_entry`)
- Cairo Arabic font + floating SnackBar (Flutter)
- KPI cards بـ inline styles (حل مشكلة الألوان المغسولة)
- `screen_inventory.py`: 729 screenshot (616 web + 113 Flutter) → PDF مضغوط 29 MB

---

## 8. الأدوار الخمسة (للفصل المفاهيمي)

| الدور | النطاق | الاهتمامات |
|-------|--------|-----------|
| Admin | الجامعة كلها | بنية تحتية، دقة التعرف، audit logs، البوابات |
| Coordinator | كليته فقط | أعذار، درجات، حضور كليته، مقاعد امتحان |
| Teacher | مقرراته | جلسات، حضور، timeline |
| Student | تسجيله | نسبة حضور، جدول، أعذار |
| Gate | البوابة | gate logs، مسح وجه، حالة قاعات |

---

## 9. مفاتيح بيئية مهمة

- adb: `C:\Users\ahmed\AppData\Local\Android\Sdk\platform-tools\adb.exe`
- flutter: `C:\develop\flutter\bin\flutter.bat` (مش في PATH)
- gh CLI: **غير مثبت** — استخدم GitHub API عبر curl + token من `git credential fill`
- emulator package: `sd.shamel.shamel`
- العمل في PowerShell على Windows؛ شاشة الإمولاتور 1080×2400
- المسار فيه عربي (`D:\مهم\`) → استخدم `python -X utf8` لتجنب cp1252 errors
- PDF inventory يُبنى في `C:\shamel_inv\` (مسار ASCII آمن)

---

## 10. النقطة المعلّقة الآن

الألوان في `admin_panel.html` تم إصلاحها بـ inline styles (commit `fcc8662`). البيانات ظاهرة بعد تشغيل server بـ `USE_LOCAL_DB=true`.

**تحقق بصرياً:** افتح `http://127.0.0.1:8000/admin-panel/` بعد Ctrl+Shift+R:
- كروت الطلاب/الأساتذة: بيضاء + أرقام داكنة واضحة
- كارت AI: أزرق داكن متدرّج + نص أبيض
- لمشاهدة بيانات الـ seed المقيّدة بالكلية: `/demo-login/?role=coordinator` ثم coordinator dashboard، أو صفحات Gate Logs / Excuse Board / Exam Seating
