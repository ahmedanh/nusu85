#!/usr/bin/env python3
"""
SHAMEL — مولّد التوثيق الشامل
==============================
يلتقط صور الشاشة لجميع الصفحات (ثيم فاتح / عربي / موبايل+ديسك) ثم يولّد:
  1. توثيق الألوان  — صورة ملونة منظّمة حسب الدور والصفحة
  2. توثيق التصميم — صورة أبيض وأسود مع تعليقات توضيحية بالعربية

المخرجات: D:\مهم\ACDC_FINAL-main\توثيق المشروع\
"""
from __future__ import annotations

import os, sys, re, time, textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright, Page, BrowserContext, Error as PWError
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display

# ─── إعدادات ──────────────────────────────────────────────────────────────────
BASE_URL  = "http://127.0.0.1:8000"
TMP_DIR   = Path("C:/shamel_docs_tmp")
OUT_DIR   = Path("D:/مهم/ACDC_FINAL-main/توثيق المشروع")
TMP_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "ديسكتوب": {"width": 1920, "height": 1080},
    "موبايل":  {"width": 390,  "height": 844},
}

ROLE_CREDS = {
    "admin":       ("admin",    "admin"),
    "coordinator": ("coord1",   "admin"),
    "teacher":     ("teacher2", "admin"),
    "student":     ("student2", "admin"),
    "gate":        ("gate1",    "admin"),
}

# ─── خريطة الدور ← اسم عربي ──────────────────────────────────────────────────
ROLE_ARABIC = {
    "public":      "عام",
    "admin":       "مدير النظام",
    "coordinator": "المنسق",
    "teacher":     "الأستاذ",
    "student":     "الطالب",
    "gate":        "حارس البوابة",
}

# ─── صفحات كل دور (اسم عربي، المسار) ────────────────────────────────────────
ROLE_ROUTES: dict[str, list[tuple[str, str]]] = {
    "public": [
        ("صفحة تسجيل الدخول",      "/login/"),
        ("تسجيل الدخول بالوجه",    "/login/face/"),
        ("حضور ناجح",              "/attendance-success/"),
        ("خطأ في الحضور",          "/attendance-error/"),
    ],
    "admin": [
        ("لوحة التحكم الرئيسية",    "/admin-panel/"),
        ("إدارة الكادر الأكاديمي", "/faculty-management/"),
        ("التقارير",               "/reports/"),
        ("تقرير حضور الطلاب",     "/reports/students/"),
        ("تقرير حضور الأساتذة",   "/reports/teachers/"),
        ("البحث الشامل",           "/search/"),
        ("الإشعارات",              "/notifications/"),
        ("الإعدادات",              "/settings/"),
        ("تقارير البوابة",         "/admin-panel/gate-reports/"),
        ("إشعارات المدير",         "/admin-panel/notifications/"),
        ("سجل التدقيق",            "/admin-panel/audit-log/"),
        ("الأقسام",                "/admin-panel/departments/"),
        ("معالج الإعداد",          "/admin-panel/onboarding/"),
        ("تقييم العمداء",          "/admin-panel/dean-evaluation/"),
        ("الجدول الزمني للكادر",  "/admin-panel/faculty-timeline/"),
        ("لوحة الأعذار",           "/admin-panel/excuse-board/"),
        ("مخطط الامتحانات",       "/admin-panel/exam-planner/"),
        ("مخطط قاعة الامتحان",    "/admin-panel/exam-seating/"),
        ("التحقق من بوابة الامتحان","/admin-panel/exam-gate/"),
        ("تذاكر الدعم",            "/admin-panel/tickets/"),
        ("قائمة المواد",           "/courses/"),
        ("إضافة مادة",             "/courses/add/"),
        ("قائمة القاعات",          "/classrooms/"),
        ("إضافة قاعة",             "/classrooms/add/"),
        ("حالة القاعات",           "/classrooms/status/"),
        ("الجدول الدراسي",        "/schedule/"),
        ("تقويم الجدول",          "/schedule/calendar/"),
        ("إضافة جدول",            "/schedule/add/"),
        ("تسجيل الوجه",           "/enroll-face/"),
        ("بوابة الدخول",          "/gate/"),
        ("تسجيل طالب",            "/faculty-management/register-student/"),
        ("تسجيل أستاذ",           "/faculty-management/register-teacher/"),
        ("الفحص الحي",            "/scan/"),
    ],
    "coordinator": [
        ("لوحة المنسق",           "/coordinator/dashboard/"),
        ("طلاب الكلية",           "/coordinator/students/"),
        ("كادر الكلية",           "/coordinator/faculty/"),
        ("توزيع المواد",          "/coordinator/assignments/"),
        ("تسجيل مستخدم",         "/coordinator/register/"),
        ("رصد الدرجات",           "/coordinator/grading/"),
        ("التقارير",              "/reports/"),
        ("تقرير حضور الطلاب",   "/reports/students/"),
        ("البحث الشامل",          "/search/"),
        ("الإشعارات",             "/notifications/"),
        ("الإعدادات",             "/settings/"),
        ("قائمة المواد",          "/courses/"),
        ("قائمة القاعات",         "/classrooms/"),
        ("الجدول الدراسي",       "/schedule/"),
        ("تذاكر الدعم",           "/admin-panel/tickets/"),
    ],
    "teacher": [
        ("لوحة الأستاذ",          "/professor-dashboard/"),
        ("المسار الزمني",         "/teacher/timeline/"),
        ("سجلات الحضور",         "/teacher/attendance-records/"),
        ("الملف الشخصي",         "/teacher/profile/"),
        ("الصلاحيات",            "/teacher/permissions/"),
        ("الجدول الدراسي",       "/schedule/"),
        ("التقارير",             "/reports/"),
        ("الإشعارات",            "/notifications/"),
        ("الإعدادات",            "/settings/"),
        ("تذاكر الدعم",          "/admin-panel/tickets/"),
        ("إنشاء تذكرة",         "/tickets/create/"),
    ],
    "student": [
        ("لوحة الطالب",          "/student/dashboard/"),
        ("الملف الشخصي",         "/student/profile/"),
        ("موادي",                "/student/courses/"),
        ("جدولي",                "/student/schedule/"),
        ("الدعم الطلابي",        "/student/support/"),
        ("بوابة الأعذار",        "/student/excuse/"),
        ("الإشعارات",            "/notifications/"),
        ("الإعدادات",            "/settings/"),
        ("إنشاء تذكرة",         "/tickets/create/"),
    ],
    "gate": [
        ("بوابة الدخول",         "/gate/"),
        ("الفحص الحي",           "/scan/"),
        ("حالة القاعات",         "/classrooms/status/"),
        ("الإشعارات",            "/notifications/"),
        ("الإعدادات",            "/settings/"),
    ],
}

# ─── أوصاف الصفحات للتوثيق التصميمي ─────────────────────────────────────────
PAGE_DESCRIPTIONS: dict[str, dict] = {
    "/login/": {
        "الوصف": "صفحة تسجيل الدخول الرئيسية للنظام",
        "العناصر": [
            "حقل اسم المستخدم — إدخال اسم المستخدم",
            "حقل كلمة المرور — إدخال كلمة المرور",
            "زر تسجيل الدخول — الدخول للنظام",
            "رابط نسيت كلمة المرور — استعادة الحساب",
            "زر تسجيل الدخول بالوجه — المصادقة البيومترية",
        ],
    },
    "/login/face/": {
        "الوصف": "صفحة تسجيل الدخول بتقنية التعرف على الوجه",
        "العناصر": [
            "نافذة الكاميرا — التقاط صورة الوجه",
            "زر بدء الفحص — تشغيل الكاميرا",
            "رابط العودة — الرجوع لتسجيل الدخول العادي",
        ],
    },
    "/admin-panel/": {
        "الوصف": "لوحة التحكم الرئيسية للمدير — إحصاءات شاملة للجامعة",
        "العناصر": [
            "بطاقات KPI — إجمالي الطلاب، الأساتذة، الحضور اليومي",
            "رسم بياني للحضور — اتجاهات الحضور الأسبوعية",
            "قائمة آخر عمليات الفحص — أحدث عمليات بوابة الدخول",
            "قائمة التنبيهات — طلبات الأعذار، التذاكر المعلقة",
            "الشريط الجانبي — روابط سريعة للأقسام",
        ],
    },
    "/coordinator/dashboard/": {
        "الوصف": "لوحة المنسق — إحصاءات أكاديمية على مستوى الكلية",
        "العناصر": [
            "بطاقات KPI — طلاب الكلية، نسبة الحضور",
            "الأعذار المعلقة — طلبات بانتظار الموافقة",
            "المواد غير المقيّمة — مواد لم تُرصد درجاتها",
            "الطلاب في خطر — من تجاوزوا حد الغياب",
        ],
    },
    "/professor-dashboard/": {
        "الوصف": "لوحة الأستاذ — إدارة المحاضرات والحضور",
        "العناصر": [
            "قائمة الجداول — محاضرات اليوم",
            "زر فتح جلسة — بدء تسجيل الحضور",
            "إحصاءات الحضور — نسب الحضور لكل مادة",
        ],
    },
    "/student/dashboard/": {
        "الوصف": "لوحة الطالب — متابعة الحضور والجدول الشخصي",
        "العناصر": [
            "نسبة الحضور — مؤشر دائري لكل مادة",
            "الجدول اليومي — محاضرات اليوم",
            "تنبيهات الغياب — تحذيرات من تجاوز الحد",
            "آخر سجلات الحضور — سجل زمني",
        ],
    },
    "/gate/": {
        "الوصف": "بوابة الدخول — مراقبة الدخول والخروج",
        "العناصر": [
            "بث الكاميرا المباشر — صورة فورية من كاميرا البوابة",
            "آخر عمليات الدخول — سجل زمني للطلاب",
            "حالة البوابة — مفتوح/مغلق",
        ],
    },
    "/scan/": {
        "الوصف": "صفحة الفحص الحي — التقاط وجوه الحضور تلقائياً",
        "العناصر": [
            "بث الكاميرا — فيديو مباشر مع تمييز الوجوه",
            "عداد الفحوصات — عدد من تم التعرف عليهم",
            "سجل الفحص — أسماء من تم رصدهم",
        ],
    },
    "/reports/": {
        "الوصف": "صفحة التقارير — تحليلات الحضور والأداء",
        "العناصر": [
            "فلتر الفترة الزمنية — تحديد نطاق التقرير",
            "رسوم بيانية — توزيع الحضور",
            "أزرار التصدير — PDF، Excel، CSV",
        ],
    },
    "/faculty-management/": {
        "الوصف": "إدارة الكادر الأكاديمي — قائمة الأساتذة والطلاب",
        "العناصر": [
            "قائمة الأساتذة — بطاقات بيانات كل أستاذ",
            "قائمة الطلاب — بطاقات بيانات كل طالب",
            "زر تسجيل أستاذ — إضافة أستاذ جديد",
            "زر تسجيل طالب — إضافة طالب جديد",
            "زر تفعيل/تعطيل الدخول — التحكم في صلاحية الدخول للطالب",
        ],
    },
    "/courses/": {
        "الوصف": "قائمة المواد الدراسية",
        "العناصر": [
            "جدول المواد — الاسم، القسم، الساعات",
            "زر إضافة مادة — مادة جديدة",
            "أزرار التعديل والحذف — لكل صف",
        ],
    },
    "/classrooms/": {
        "الوصف": "قائمة القاعات الدراسية",
        "العناصر": [
            "جدول القاعات — الاسم، السعة، الموقع",
            "زر إضافة قاعة — قاعة جديدة",
            "أزرار التعديل والحذف",
        ],
    },
    "/classrooms/status/": {
        "الوصف": "حالة القاعات في الوقت الفعلي",
        "العناصر": [
            "بطاقات القاعات — شاغلة/فارغة مع اللون",
            "عدد الطلاب الحاليين في كل قاعة",
            "آخر تحديث — وقت آخر فحص",
        ],
    },
    "/schedule/": {
        "الوصف": "الجدول الدراسي الأسبوعي",
        "العناصر": [
            "جدول أسبوعي — أيام × فترات زمنية",
            "زر إضافة محاضرة — جدولة جديدة",
            "رمز كل مادة — اللون والأستاذ والقاعة",
        ],
    },
    "/admin-panel/excuse-board/": {
        "الوصف": "لوحة الأعذار — مراجعة وقبول أعذار الغياب",
        "العناصر": [
            "قائمة الأعذار المعلقة — اسم الطالب، سبب الغياب، المرفق",
            "زر قبول — الموافقة على العذر",
            "زر رفض — رفض العذر",
        ],
    },
    "/admin-panel/tickets/": {
        "الوصف": "تذاكر الدعم الفني",
        "العناصر": [
            "قائمة التذاكر — العنوان، الحالة، المقدم",
            "فلتر الحالة — مفتوح/مغلق/معلق",
            "زر عرض التفاصيل — فتح التذكرة",
        ],
    },
    "/notifications/": {
        "الوصف": "مركز الإشعارات الشخصية",
        "العناصر": [
            "قائمة الإشعارات — الرسالة، الوقت، النوع",
            "زر تحديد الكل كمقروء",
            "أيقونة النوع — تنبيه، معلومة، خطأ",
        ],
    },
    "/settings/": {
        "الوصف": "إعدادات الحساب والنظام",
        "العناصر": [
            "تغيير كلمة المرور — حقول كلمة المرور الجديدة",
            "تفضيلات اللغة — عربي/إنجليزي",
            "تفضيلات الثيم — فاتح/داكن",
            "زر حفظ التغييرات",
        ],
    },
    "/search/": {
        "الوصف": "البحث الشامل في النظام",
        "العناصر": [
            "حقل البحث — نص البحث",
            "فلتر النوع — طالب، أستاذ، مادة",
            "نتائج البحث — قائمة مرتبة",
        ],
    },
    "/student/excuse/": {
        "الوصف": "بوابة تقديم الأعذار للطالب",
        "العناصر": [
            "اختيار المادة — قائمة منسدلة",
            "اختيار التاريخ — يوم الغياب",
            "حقل السبب — وصف العذر",
            "زر رفع المستند — مرفق العذر",
            "زر إرسال",
        ],
    },
    "/admin-panel/audit-log/": {
        "الوصف": "سجل التدقيق — كل الأحداث والتعديلات",
        "العناصر": [
            "جدول الأحداث — المستخدم، الإجراء، الوقت",
            "فلتر التاريخ والمستخدم",
            "تصدير السجل",
        ],
    },
    "/admin-panel/departments/": {
        "الوصف": "إدارة الأقسام الأكاديمية",
        "العناصر": [
            "قائمة الأقسام — الاسم، الكلية، عدد الطلاب",
            "زر إضافة قسم",
            "أزرار التعديل والحذف",
        ],
    },
    "/admin-panel/exam-planner/": {
        "الوصف": "مخطط الامتحانات",
        "العناصر": [
            "تقويم الامتحانات — المادة، التاريخ، القاعة",
            "زر إضافة امتحان",
            "تصدير الجدول",
        ],
    },
    "/admin-panel/exam-seating/": {
        "الوصف": "مخطط جلوس الامتحان",
        "العناصر": [
            "مخطط القاعة — مواضع المقاعد",
            "اسم الطالب على كل مقعد",
            "طباعة المخطط",
        ],
    },
    "/admin-panel/dean-evaluation/": {
        "الوصف": "تقييم العمداء والكليات",
        "العناصر": [
            "تصنيف الكليات — حسب نسبة الحضور",
            "رسوم بيانية مقارنة",
            "تصدير التقرير",
        ],
    },
    "/admin-panel/faculty-timeline/": {
        "الوصف": "المسار الزمني للكادر الأكاديمي",
        "العناصر": [
            "مسار زمني تفاعلي — أنشطة الأساتذة",
            "فلتر الأستاذ والفترة",
        ],
    },
    "/admin-panel/onboarding/": {
        "الوصف": "معالج الإعداد الأولي للنظام",
        "العناصر": [
            "خطوات متعددة — إعداد الكلية، الأقسام، المواد",
            "شريط التقدم",
            "أزرار التالي والسابق",
        ],
    },
    "/enroll-face/": {
        "الوصف": "تسجيل بيانات الوجه البيومترية",
        "العناصر": [
            "قائمة الأشخاص — طلاب وأساتذة غير مسجلين",
            "زر بدء التسجيل — تشغيل الكاميرا",
            "شريط التقدم — عدد الإطارات المسجلة",
        ],
    },
    "/teacher/attendance-records/": {
        "الوصف": "سجلات حضور الأستاذ",
        "العناصر": [
            "قائمة الجلسات — التاريخ، المادة، عدد الحضور",
            "تفاصيل الجلسة — أسماء الحضور والغائبين",
            "تصدير السجل",
        ],
    },
    "/teacher/timeline/": {
        "الوصف": "المسار الزمني للأستاذ",
        "العناصر": [
            "مسار زمني — الجلسات المفتوحة والمغلقة",
            "حالة كل جلسة — نسبة الحضور",
        ],
    },
    "/teacher/profile/": {
        "الوصف": "الملف الشخصي للأستاذ",
        "العناصر": [
            "البيانات الشخصية — الاسم، القسم",
            "المواد المسندة — قائمة المواد",
            "إحصاءات الحضور الإجمالية",
        ],
    },
    "/teacher/permissions/": {
        "الوصف": "صلاحيات الأستاذ",
        "العناصر": [
            "قائمة الطلاب — التفعيل/التعطيل لكل طالب",
            "زر حفظ التغييرات",
        ],
    },
    "/coordinator/students/": {
        "الوصف": "طلاب الكلية",
        "العناصر": [
            "جدول الطلاب — الاسم، الرقم، القسم، نسبة الحضور",
            "فلتر القسم",
            "تصدير قائمة الطلاب",
        ],
    },
    "/coordinator/faculty/": {
        "الوصف": "كادر الكلية الأكاديمي",
        "العناصر": [
            "قائمة الأساتذة — الاسم، القسم، المواد",
            "إحصاءات أداء كل أستاذ",
        ],
    },
    "/coordinator/assignments/": {
        "الوصف": "توزيع المواد على الأساتذة",
        "العناصر": [
            "جدول التوزيع — المادة، الأستاذ، الفصل",
            "زر تعديل التوزيع",
        ],
    },
    "/coordinator/grading/": {
        "الوصف": "رصد الدرجات",
        "العناصر": [
            "قائمة المواد — المواد غير المرصودة",
            "زر رصد الدرجات — فتح نموذج الإدخال",
        ],
    },
    "/student/profile/": {
        "الوصف": "الملف الشخصي للطالب",
        "العناصر": [
            "البيانات الشخصية — الاسم، الرقم الجامعي",
            "نسب الحضور — لكل مادة",
            "الحالة الأكاديمية",
        ],
    },
    "/student/courses/": {
        "الوصف": "المواد الدراسية للطالب",
        "العناصر": [
            "قائمة المواد — الاسم، الأستاذ، نسبة الحضور",
            "مؤشر اللون — أخضر/أصفر/أحمر حسب النسبة",
        ],
    },
    "/student/schedule/": {
        "الوصف": "الجدول الدراسي الشخصي للطالب",
        "العناصر": [
            "جدول أسبوعي — المواد والقاعات",
            "تمييز محاضرات اليوم",
        ],
    },
    "/student/support/": {
        "الوصف": "الدعم الطلابي",
        "العناصر": [
            "روابط الدعم — FAQ، تواصل مع الإدارة",
            "إنشاء تذكرة دعم",
        ],
    },
    "/tickets/create/": {
        "الوصف": "إنشاء تذكرة دعم فني",
        "العناصر": [
            "حقل العنوان",
            "حقل الوصف التفصيلي",
            "اختيار الأولوية",
            "زر إرسال التذكرة",
        ],
    },
    "/attendance-success/": {
        "الوصف": "صفحة تأكيد تسجيل الحضور بنجاح",
        "العناصر": [
            "أيقونة نجاح — علامة صح خضراء",
            "اسم الطالب المسجَّل",
            "وقت التسجيل",
        ],
    },
    "/attendance-error/": {
        "الوصف": "صفحة خطأ تسجيل الحضور",
        "العناصر": [
            "أيقونة خطأ — علامة ✗ حمراء",
            "رسالة الخطأ",
            "زر المحاولة مجدداً",
        ],
    },
    "/admin-panel/gate-reports/": {
        "الوصف": "تقارير البوابة التفصيلية",
        "العناصر": [
            "إحصاءات دخول يومية",
            "رسم بياني للدخول حسب الساعة",
            "قائمة المنبوذين — من رُفض دخولهم",
        ],
    },
    "/admin-panel/notifications/": {
        "الوصف": "مركز الإشعارات للمدير",
        "العناصر": [
            "إشعارات فورية — بث WebSocket",
            "فلتر نوع الإشعار",
        ],
    },
    "/admin-panel/exam-gate/": {
        "الوصف": "التحقق من هوية الطالب عند بوابة الامتحان",
        "العناصر": [
            "حقل البحث عن الطالب",
            "بيانات الطالب — الصورة، الاسم، الرقم",
            "حالة التسجيل — مسموح/ممنوع",
        ],
    },
    "/coordinator/register/": {
        "الوصف": "تسجيل مستخدم جديد (من قِبل المنسق)",
        "العناصر": [
            "نموذج بيانات المستخدم",
            "اختيار الدور — طالب/أستاذ",
            "زر إنشاء الحساب",
        ],
    },
    "/courses/add/": {
        "الوصف": "إضافة مادة دراسية جديدة",
        "العناصر": [
            "حقل اسم المادة",
            "اختيار القسم",
            "عدد الساعات",
            "زر حفظ",
        ],
    },
    "/classrooms/add/": {
        "الوصف": "إضافة قاعة دراسية جديدة",
        "العناصر": [
            "حقل اسم القاعة",
            "حقل الموقع",
            "حقل السعة",
            "زر حفظ",
        ],
    },
    "/schedule/add/": {
        "الوصف": "إضافة جدول دراسي جديد",
        "العناصر": [
            "اختيار المادة والأستاذ والقاعة",
            "اليوم والوقت",
            "زر حفظ",
        ],
    },
    "/schedule/calendar/": {
        "الوصف": "تقويم الجدول الدراسي",
        "العناصر": [
            "عرض تقويمي أسبوعي",
            "النقر على فترة زمنية لإضافة محاضرة",
            "تلوين حسب المادة",
        ],
    },
    "/faculty-management/register-student/": {
        "الوصف": "معالج تسجيل طالب جديد",
        "العناصر": [
            "خطوة 1: البيانات الشخصية",
            "خطوة 2: بيانات القبول",
            "خطوة 3: تسجيل الوجه",
            "شريط التقدم",
        ],
    },
    "/faculty-management/register-teacher/": {
        "الوصف": "معالج تسجيل أستاذ جديد",
        "العناصر": [
            "خطوة 1: البيانات الشخصية",
            "خطوة 2: القسم والمؤهل",
            "خطوة 3: تسجيل الوجه",
            "شريط التقدم",
        ],
    },
}

# ─── دالة مساعدة: إعادة تشكيل النص العربي للرسم ─────────────────────────────
def ar(text: str) -> str:
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text

# ─── تحميل الخط العربي ───────────────────────────────────────────────────────
def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/ArialUni.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for fp in candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ─── رسم التوثيق التصميمي (أبيض وأسود مع تعليقات) ───────────────────────────
def create_wireframe(png_path: Path, page_name: str, page_path: str, role_ar: str) -> Image.Image:
    """تحويل صورة الشاشة الملونة إلى توثيق تصميمي مشروح"""
    img = Image.open(png_path).convert("RGB")
    W, H = img.size

    # تحويل لأبيض وأسود مع تعزيز الحواف
    gray = ImageOps.grayscale(img)
    enhanced = ImageEnhance.Contrast(gray).enhance(1.5)
    # تحويل لأبيض وأسود ثنائي (threshold)
    bw = enhanced.point(lambda x: 255 if x > 140 else 0)
    wireframe = bw.convert("RGB")

    # إضافة منطقة التعليقات (padding أسفل الصورة)
    pad = 280
    canvas = Image.new("RGB", (W, H + pad), (255, 255, 255))
    canvas.paste(wireframe, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # إطار الصورة
    draw.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0), width=3)

    # قسم التعليقات
    draw.rectangle([0, H, W, H + pad], fill=(245, 245, 245), outline=(0, 0, 0), width=2)

    # خط فاصل
    draw.line([(20, H + 10), (W - 20, H + 10)], fill=(180, 180, 180), width=1)

    f_title  = load_font(22)
    f_label  = load_font(16)
    f_small  = load_font(13)

    # عنوان الصفحة (يمين → يسار)
    title_text = ar(f"🔷 {page_name}")
    draw.text((W - 20, H + 20), title_text, fill=(0, 0, 180), font=f_title, anchor="ra")

    # الدور
    role_text = ar(f"الدور: {role_ar}  |  المسار: {page_path}")
    draw.text((W - 20, H + 50), role_text, fill=(80, 80, 80), font=f_small, anchor="ra")

    # الوصف
    desc_info = PAGE_DESCRIPTIONS.get(page_path, {})
    desc = desc_info.get("الوصف", "—")
    draw.text((W - 20, H + 75), ar(f"الوصف: {desc}"), fill=(0, 0, 0), font=f_label, anchor="ra")

    # العناصر
    elements = desc_info.get("العناصر", [])
    y = H + 100
    for i, elem in enumerate(elements[:6]):  # max 6 عناصر
        draw.text((W - 30, y), ar(f"◆ {elem}"), fill=(30, 100, 30), font=f_small, anchor="ra")
        y += 25

    # إطار مميز للتوثيق
    draw.rectangle([2, 2, W - 3, H - 3], outline=(0, 0, 200), width=2)

    return canvas

# ─── مصادقة ──────────────────────────────────────────────────────────────────
def login(page: Page, username: str, password: str) -> bool:
    try:
        page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded", timeout=20_000)
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("domcontentloaded", timeout=15_000)
        return "/login" not in page.url
    except PWError:
        return False


def ensure_session(ctx: BrowserContext, role: str) -> Page:
    page = ctx.new_page()
    try:
        page.goto(f"{BASE_URL}/demo-login/?role={role}", wait_until="domcontentloaded", timeout=20_000)
        if "/login" not in page.url:
            return page
    except PWError:
        pass
    if role in ROLE_CREDS:
        u, p = ROLE_CREDS[role]
        login(page, u, p)
    return page


def set_light_arabic(page: Page) -> None:
    page.evaluate("""() => {
        const h = document.documentElement;
        h.classList.remove('dark'); h.classList.add('light');
        try { localStorage.setItem('theme','light'); } catch(e){}
        document.documentElement.lang = 'ar';
        document.documentElement.dir  = 'rtl';
        try { localStorage.setItem('lang','ar'); } catch(e){}
    }""")


def capture_page(page: Page, path: str, vp: dict, out_path: Path) -> Optional[str]:
    url = BASE_URL + path
    try:
        page.set_viewport_size(vp)
        if "scan" in path or "video_feed" in path or "notifications" in path or "live-stats" in path:
            page.goto(url, wait_until="commit", timeout=20_000)
        else:
            page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        set_light_arabic(page)
        time.sleep(0.4)
        page.screenshot(path=str(out_path), full_page=False)
        return None
    except Exception as e:
        return str(e)


# ─── البرنامج الرئيسي ─────────────────────────────────────────────────────────
def main():
    print("═" * 60)
    print("  SHAMEL — مولّد التوثيق الشامل")
    print("═" * 60)

    # إنشاء هيكل المجلدات
    folders = {
        "عام":              OUT_DIR / "01_عام",
        "مدير النظام":     OUT_DIR / "02_مدير_النظام",
        "المنسق":          OUT_DIR / "03_المنسق",
        "الأستاذ":         OUT_DIR / "04_الأستاذ",
        "الطالب":          OUT_DIR / "05_الطالب",
        "حارس البوابة":   OUT_DIR / "06_حارس_البوابة",
    }

    for name, folder in folders.items():
        (folder / "ديسكتوب" / "ملون").mkdir(parents=True, exist_ok=True)
        (folder / "ديسكتوب" / "تصميم").mkdir(parents=True, exist_ok=True)
        (folder / "موبايل" / "ملون").mkdir(parents=True, exist_ok=True)
        (folder / "موبايل" / "تصميم").mkdir(parents=True, exist_ok=True)

    ROLE_TO_FOLDER = {
        "public":      OUT_DIR / "01_عام",
        "admin":       OUT_DIR / "02_مدير_النظام",
        "coordinator": OUT_DIR / "03_المنسق",
        "teacher":     OUT_DIR / "04_الأستاذ",
        "student":     OUT_DIR / "05_الطالب",
        "gate":        OUT_DIR / "06_حارس_البوابة",
    }

    total = sum(len(v) for v in ROLE_ROUTES.values()) * 2  # 2 viewports
    done = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--disable-web-security"])

        for role, routes in ROLE_ROUTES.items():
            role_ar = ROLE_ARABIC[role]
            folder  = ROLE_TO_FOLDER[role]
            print(f"\n── {role_ar} ──────────────────────────")

            for vp_name, vp in VIEWPORTS.items():
                ctx = browser.new_context(
                    viewport=vp,
                    locale="ar",
                    extra_http_headers={"Accept-Language": "ar,en;q=0.5"},
                )
                ctx.add_init_script("""() => {
                    localStorage.setItem('theme','light');
                    localStorage.setItem('lang','ar');
                }""")

                page = ensure_session(ctx, role) if role != "public" else ctx.new_page()

                for page_name, path in routes:
                    done += 1
                    safe_name = re.sub(r'[\\/*?:"<>|]', '_', page_name)
                    tmp_png   = TMP_DIR / f"{role}_{vp_name}_{safe_name}.png"

                    err = capture_page(page, path, vp, tmp_png)
                    if err:
                        print(f"  ✗ [{vp_name}] {page_name}: {err[:60]}")
                        continue

                    # حفظ الصورة الملونة
                    colored_out = folder / vp_name / "ملون" / f"{safe_name}.png"
                    import shutil
                    shutil.copy2(tmp_png, colored_out)

                    # إنشاء وحفظ التوثيق التصميمي
                    try:
                        wire = create_wireframe(tmp_png, page_name, path, role_ar)
                        wire_out = folder / vp_name / "تصميم" / f"{safe_name}_تصميم.png"
                        wire.save(str(wire_out))
                        print(f"  ✓ [{vp_name}] {page_name}  ({done}/{total})")
                    except Exception as ex:
                        print(f"  ⚠ [{vp_name}] {page_name} wireframe error: {ex}")

                ctx.close()

        browser.close()

    # ─── ملف الفهرس ───────────────────────────────────────────────────────────
    index_lines = [
        "# فهرس توثيق مشروع شامل\n",
        f"**تاريخ التوثيق:** 2026-06-04\n",
        "**الثيم:** فاتح | **اللغة:** عربي\n\n",
        "---\n\n",
    ]

    folder_map = {
        "01_عام":            ("عام", "public"),
        "02_مدير_النظام":   ("مدير النظام", "admin"),
        "03_المنسق":        ("المنسق", "coordinator"),
        "04_الأستاذ":       ("الأستاذ", "teacher"),
        "05_الطالب":        ("الطالب", "student"),
        "06_حارس_البوابة": ("حارس البوابة", "gate"),
    }

    for folder_name, (ar_name, role) in folder_map.items():
        index_lines.append(f"## {ar_name}\n\n")
        for page_name, path in ROLE_ROUTES.get(role, []):
            safe = re.sub(r'[\\/*?:"<>|]', '_', page_name)
            desc = PAGE_DESCRIPTIONS.get(path, {}).get("الوصف", "—")
            index_lines.append(f"### {page_name}\n")
            index_lines.append(f"- **المسار:** `{path}`\n")
            index_lines.append(f"- **الوصف:** {desc}\n")
            index_lines.append(f"- 🖥️ [ديسكتوب ملون](./{folder_name}/ديسكتوب/ملون/{safe}.png)\n")
            index_lines.append(f"- 🎨 [ديسكتوب تصميم](./{folder_name}/ديسكتوب/تصميم/{safe}_تصميم.png)\n")
            index_lines.append(f"- 📱 [موبايل ملون](./{folder_name}/موبايل/ملون/{safe}.png)\n")
            index_lines.append(f"- 🔲 [موبايل تصميم](./{folder_name}/موبايل/تصميم/{safe}_تصميم.png)\n\n")

    index_path = OUT_DIR / "فهرس_التوثيق.md"
    index_path.write_text("".join(index_lines), encoding="utf-8")

    print(f"\n{'═'*60}")
    print(f"  ✅ اكتمل التوثيق!")
    print(f"  📁 المجلد: {OUT_DIR}")
    print(f"  📄 الفهرس: {index_path}")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
