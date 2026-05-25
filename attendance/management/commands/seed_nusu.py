"""
seed_nusu.py  –  Seed the National University Sudan database
Usage:
  python manage.py seed_nusu              # add data (safe, skips existing)
  python manage.py seed_nusu --fresh      # wipe relevant tables first

Targets:
  • 12 Colleges (exact, from document)
  • Departments per college
  • 887 Courses  (from document + generated extras)
  • 399 Teachers (random Sudanese names)
  • 9889 Students (random Sudanese names)
  • Gate users:  gf1–gf15
  • Teacher auth users: tf1–tf3
  • Student auth users: sf1–sf3
  • 1 Coordinator per college
"""

import random
import uuid
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import (
    College, Department, Course, Teacher, Student, Coordinator
)

# ──────────────────────────────────────────────────────────────────────────────
# PASSWORDS
# ──────────────────────────────────────────────────────────────────────────────
GATE_PWD  = 'Gate@NUSU2026!'
TEACHER_PWD = 'Teacher@NUSU2026!'
STUDENT_PWD = 'Student@NUSU2026!'
COORD_PWD   = 'Coord@NUSU2026!'

# ──────────────────────────────────────────────────────────────────────────────
# COLLEGES (12 exact)
# ──────────────────────────────────────────────────────────────────────────────
COLLEGES = [
    ('GEN', 'الكلية التأسيسية العامة',                     'General Foundation College'),
    ('MED', 'كلية الطب والجراحة',                          'College of Medicine & Surgery'),
    ('PHA', 'كلية الصيدلة السريرية والصناعية',             'College of Clinical & Industrial Pharmacy'),
    ('DEN', 'كلية طب وجراحة الأسنان',                     'College of Dentistry'),
    ('RAD', 'كلية علوم الراديوجرافيا والتصوير الطبي',     'College of Radiography & Medical Imaging'),
    ('MLS', 'كلية علوم المختبرات الطبية',                  'College of Medical Laboratory Sciences'),
    ('PHY', 'كلية العلاج الطبيعي',                         'College of Physical Therapy'),
    ('CSI', 'كلية علوم الحاسوب وتقنية المعلومات',          'College of Computer Science & IT'),
    ('ADM', 'كلية العلوم الإدارية',                        'College of Administrative Sciences'),
    ('ENG', 'كلية الهندسة والعمارة',                       'College of Engineering & Architecture'),
    ('NUR', 'كلية علوم التمريض والتوليد',                  'College of Nursing & Midwifery'),
    ('IRD', 'العلاقات الدولية والدراسات الدبلوماسية',      'College of International Relations & Diplomatic Studies'),
]

# ──────────────────────────────────────────────────────────────────────────────
# DEPARTMENTS per college code
# ──────────────────────────────────────────────────────────────────────────────
DEPARTMENTS = {
    'GEN': ['مسار العلوم الأساسية المشترك'],
    'MED': ['الطب والجراحة العامة'],
    'PHA': ['الصيدلة العامة', 'الصيدلة السريرية', 'الصيدلة الصناعية'],
    'DEN': ['طب وجراحة الأسنان'],
    'RAD': ['التصوير الطبي والأشعة', 'التصوير بالموجات فوق الصوتية'],
    'MLS': ['علوم المختبرات الطبية', 'الأحياء الدقيقة الطبية'],
    'PHY': ['العلاج الطبيعي', 'إعادة التأهيل'],
    'CSI': ['علوم الحاسوب (CS)', 'تقنية المعلومات (IT)'],
    'ADM': ['تخصص المحاسبة', 'تخصص التسويق', 'إدارة الأعمال', 'نظم المعلومات الإدارية (MIS)'],
    'ENG': ['الهندسة المدنية', 'الهندسة الكهربائية والإلكترونية', 'الهندسة المعمارية'],
    'NUR': ['التمريض العام', 'التوليد وصحة الأم'],
    'IRD': ['العلاقات الدولية (IR)', 'الدراسات الدبلوماسية (DS)'],
}

# ──────────────────────────────────────────────────────────────────────────────
# COURSES from document  (title, code, college_code, year_level)
# ──────────────────────────────────────────────────────────────────────────────
DOC_COURSES = [
    # ── General Foundation ──────────────────────────────────────────────────
    ('Introduction to Medicine & Med. Education', 'GEN-101', 'GEN', 1),
    ('Computer Science -1',                        'GEN-102', 'GEN', 1),
    ('English Language',                           'GEN-103', 'GEN', 1),
    ('Basic Biochemistry',                         'GEN-104', 'GEN', 1),
    ('Biostatistics',                              'GEN-105', 'GEN', 1),
    ('Introduction to Medical Ethics',             'GEN-106', 'GEN', 1),
    ('Behavioral Science',                         'GEN-107', 'GEN', 1),
    ('Man and His Environment',                    'GEN-108', 'GEN', 1),

    # ── Medicine & Surgery ──────────────────────────────────────────────────
    ('General Histology',                          'ME-HIST-111', 'MED', 1),
    ('Human Body Structure & Function 1',          'ME-HBSF-112', 'MED', 1),
    ('Physics (Medical)',                          'ME-PHYS-113', 'MED', 1),
    ('English (Medical Specialization)',           'ME-ENGL-114', 'MED', 1),
    ('ME-ENV-127 (Man & Environment)',             'ME-ENV-127',  'MED', 1),
    ('English 2 Medical',                          'ME-ENGL-128', 'MED', 1),
    ('Genetics & Molecular Biology',               'ME-GEN-129',  'MED', 1),
    ('Basic Epidemiology',                         'ME-EPI-211',  'MED', 2),
    ('ME-BPHARM-217 (Pharmaceutical Chemistry)',   'ME-BPHARM-217','MED', 2),
    ('ME-HEM-316 (Hematology & Lymphology)',       'ME-HEM-316',  'MED', 2),
    ('ME-CVS-214 (Cardiovascular & Respiratory)',  'ME-CVS-214',  'MED', 2),
    ('ME-SKILL-221 (Professional & Clinical Skills)','ME-SKILL-221','MED', 2),
    ('ME-PHC-215 (Basic Pharmacology)',            'ME-PHC-215',  'MED', 2),
    ('ME-MSK-223 (Musculoskeletal System)',        'ME-MSK-223',  'MED', 2),
    ('ME-NUT-224 (Clinical Nutrition)',            'ME-NUT-224',  'MED', 2),
    ('ME-GIT-225 (Gastrointestinal & Urinary)',    'ME-GIT-225',  'MED', 2),
    ('ME-EPI-312 (Clinical Epidemiology)',         'ME-EPI-312',  'MED', 2),
    ('ME-ENDO-315 (Endocrinology & Reproduction)', 'ME-ENDO-315', 'MED', 3),
    ('ME-SKILL-321 (Professional Skills 3)',       'ME-SKILL-321','MED', 3),
    ('ME-HAN-322 (Applied Human Anatomy)',         'ME-HAN-322',  'MED', 3),
    ('ME-CNS-323 (Central Nervous System)',        'ME-CNS-323',  'MED', 3),
    ('ME-TROP-324 (Tropical & Infectious Diseases)','ME-TROP-324','MED', 3),
    ('ME-CPHARM-325 (Clinical Pharmacology)',      'ME-CPHARM-325','MED', 3),
    ('Ophthalmology - Medicine',                   'ME-OPH-411',  'MED', 4),
    ('ME-MER-412 (Clinical Medical Research)',     'ME-MER-412',  'MED', 4),
    ('Obstetric and Gynecology',                   'ME-OBGY-511', 'MED', 5),
    ('Pediatric (Clinical)',                       'ME-PED-512',  'MED', 5),
    ('ME-LAW-522 (Forensic Medicine)',             'ME-LAW-522',  'MED', 5),
    ('Pathology & Histopathology',                 'ME-PATH-311', 'MED', 3),
    ('Community Medicine',                         'ME-COMM-411', 'MED', 4),
    ('Psychiatry',                                 'ME-PSYC-421', 'MED', 4),
    ('Internal Medicine',                          'ME-INT-422',  'MED', 4),
    ('Surgery',                                    'ME-SURG-423', 'MED', 4),
    ('Ear Nose Throat (ENT)',                      'ME-ENT-511',  'MED', 5),

    # ── Pharmacy ─────────────────────────────────────────────────────────────
    ('PA-ORG-119 (Organic Chemistry 1)',            'PA-ORG-119',  'PHA', 1),
    ('PA-DIS-126 (Anatomy & Physiology)',           'PA-DIS-126',  'PHA', 1),
    ('PA-GEN-127 (Cellular & Pharmaceutical Genetics)','PA-GEN-127','PHA', 1),
    ('Human Body Structure & Functions-2',         'PA-HBSF-128', 'PHA', 1),
    ('Microbiology & Proctology',                  'PA-MICR-129', 'PHA', 1),
    ('Basic Biochemistry (Pharmacy)',               'PA-BIOC-130', 'PHA', 1),
    ('Organic Chemistry 2',                        'PA-ORG-211',  'PHA', 2),
    ('Pharmacology 1',                             'PA-PHAR-212', 'PHA', 2),
    ('PA-CHEM-217 (Pharmaceutical Chemistry)',      'PA-CHEM-217', 'PHA', 2),
    ('PA-METAB-214 (Biochemistry & Metabolism)',    'PA-METAB-214','PHA', 2),
    ('PA-NUPR-226 (Nutrition & Pharmaceutical Care)','PA-NUPR-226','PHA', 2),
    ('Communication Skills',                       'PA-COMM-213', 'PHA', 2),
    ('Laboratory Skills-1',                        'PA-LAB-221',  'PHA', 2),
    ('Pharmacognosy & Plant Sciences -1',          'PA-PGNO-222', 'PHA', 2),
    ('Pharmacology -2',                            'PA-PHAR-223', 'PHA', 2),
    ('Medicinal Chemistry-1',                      'PA-MCHE-224', 'PHA', 2),
    ('Pharmacognosy & Plant Sciences -2',          'PA-PGNO-225', 'PHA', 2),
    ('Pharmaceutical Microbiology-1',              'PA-PMIC-226', 'PHA', 2),
    ('Physical Pharmacy',                          'PA-PHPH-311', 'PHA', 3),
    ('Pharmacy Practice-1',                        'PA-PRAC-312', 'PHA', 3),
    ('Powder Technology',                          'PA-POWD-313', 'PHA', 3),
    ('Laboratory Skills 2',                        'PA-LAB-314',  'PHA', 3),
    ('Pharmaceutical Microbiology-2',              'PA-PMIC-315', 'PHA', 3),
    ('Pa-Epic (Pharmaceutical Epidemiology)',       'PA-EPIC-316', 'PHA', 3),
    ('Pharmaco-Informatics',                       'PA-INFO-321', 'PHA', 3),
    ('Dosage Form Design',                         'PA-DOSE-322', 'PHA', 3),
    ('PA-TREAT-325 (Pharmaceutical Therapeutics)', 'PA-TREAT-325','PHA', 3),
    ('Pharmacy Practice-2',                        'PA-PRAC-326', 'PHA', 3),
    ('Introduction To Clinical Pharmacy',          'PA-CPHI-327', 'PHA', 3),
    ('Drug Supply Management',                     'PA-DGSM-328', 'PHA', 3),
    ('Analysis 2 (Instrumental Pharmaceutical)',   'PA-ANAL-411', 'PHA', 4),
    ('PA-QUAL-426 (Quality Control & Assurance)',  'PA-QUAL-426', 'PHA', 4),
    ('PA-PAC-424 (Packaging Technology)',          'PA-PAC-424',  'PHA', 4),
    ('PA-MARK-414 (Pharmaceutical Marketing)',     'PA-MARK-414', 'PHA', 4),
    ('PA-RDU-427 (Rational Drug Use)',             'PA-RDU-427',  'PHA', 4),
    ('PA-DAB-411 (Drug Abuse & Toxicology)',       'PA-DAB-411',  'PHA', 4),
    ('PA-REC-429 (Medical Research Methodology)',  'PA-REC-429',  'PHA', 4),
    ('Orthopedics (Pharmacy)',                     'PA-ORTH-421', 'PHA', 4),
    ('Ethics (Pharmaceutical Practice)',           'PA-ETH-422',  'PHA', 4),
    ('PA-SURG-414 (Surgery for Pharmacy)',         'PA-SURG-414', 'PHA', 4),
    ('Dermatology',                                'PA-DERM-423', 'PHA', 4),
    ('Internal Medicine (Pharmacy)',               'PA-INTM-424', 'PHA', 4),
    ('Chest and Cardio',                           'PA-CHST-425', 'PHA', 4),
    ('Emergency Medicine (Pharmacy)',              'PA-EMRG-426', 'PHA', 4),
    ('Ophthalmology (Pharmacy)',                   'PA-OPTH-427', 'PHA', 4),
    ('Family Medicine',                            'PA-FAMM-511', 'PHA', 5),
    ('Pediatrics (Pharmacy)',                      'PA-PED-512',  'PHA', 5),
    ('Ear, Nose And Throat (Pharmacy)',            'PA-ENT-513',  'PHA', 5),
    ('Obstetrics & Gynecology (Pharmacy)',         'PA-OBGY-514', 'PHA', 5),
    ('Psychiatry (Pharmacy)',                      'PA-PSYC-515', 'PHA', 5),
    ('Marketing (Pharmaceutical)',                 'PA-MRKT-516', 'PHA', 5),
    ('Pa-Stab-527 (Drug System Stability)',        'PA-STAB-527', 'PHA', 5),
    ('Biopharmaceutics & Pharmacokinetics',        'PA-BPKN-521', 'PHA', 5),
    ('Medicinal Chemistry 2 (Clinical)',           'PA-MCHE-522', 'PHA', 5),
    ('CDMD (Drug & Therapeutic Systems Development)','PA-CDMD-523','PHA', 5),
    ('Pa-Drug (Clinical Pharmacology & Toxicology)','PA-DRUG-524','PHA', 5),

    # ── Dentistry ────────────────────────────────────────────────────────────
    ('DE-STAT-117 (Dental Medical Statistics)',    'DE-STAT-117', 'DEN', 1),
    ('DE-TERM-312 (Medical Terminology Dentistry)','DE-TERM-312', 'DEN', 2),
    ('DE-SKILL-211 (Professional Skills Dentistry)','DE-SKILL-211','DEN', 2),
    ('DE-HEM-316 (Blood & Lymphatic Diseases)',    'DE-HEM-316',  'DEN', 2),
    ('DE-REC-227 (Academic Research & Documentation)','DE-REC-227','DEN', 2),
    ('DE-HAN-214 (Head & Neck Anatomy)',           'DE-HAN-214',  'DEN', 2),
    ('Professional Skill III',                     'DE-SKILL-311','DEN', 3),
    ('Dental and Oral Pathology 1',                'DE-PATH-312', 'DEN', 3),
    ('Dental and Oral Microbiology',               'DE-MICR-313', 'DEN', 3),
    ('Prosthodontics-1',                           'DE-PROS-314', 'DEN', 3),
    ('Dental Materials',                           'DE-MATL-315', 'DEN', 3),
    ('DE-PHARM-312 (Oral & Dental Drugs)',         'DE-PHARM-312','DEN', 3),
    ('General Medicine (Dentistry)',               'DE-GENM-316', 'DEN', 3),
    ('DE-SKILL-311 (Clinical Skills 4)',           'DE-SKILL-321','DEN', 3),
    ('Dental and Oral Pathology 2',                'DE-PATH-322', 'DEN', 3),
    ('DE-SURG-421 (Oral & Dental Surgery Basics)', 'DE-SURG-421', 'DEN', 3),
    ('DE-DPH-323 (General Dental Health)',         'DE-DPH-323',  'DEN', 3),
    ('Prosthodontics-2',                           'DE-PROS-411', 'DEN', 4),
    ('Maxillofacial Surgery-1',                    'DE-MXFS-412', 'DEN', 4),
    ('DE-OMED-424 (Comprehensive Oral Medicine)',  'DE-OMED-424', 'DEN', 4),
    ('Periodontics-1',                             'DE-PERI-413', 'DEN', 4),
    ('Oral Hygiene',                               'DE-HYGN-414', 'DEN', 4),
    ('Conservative Dentistry-1',                   'DE-CONS-415', 'DEN', 4),
    ('Endodontics',                                'DE-ENDO-416', 'DEN', 4),
    ('Pedodontics',                                'DE-PEDO-417', 'DEN', 4),
    ('Orthodontics',                               'DE-ORTH-418', 'DEN', 4),

    # ── Radiography ──────────────────────────────────────────────────────────
    ('Radiation Physics 1',                        'RAD-PHYS-111','RAD', 1),
    ('Mathematics (Radiology)',                    'RAD-MATH-112','RAD', 1),
    ('MUSY (Musculoskeletal Imaging Foundation)',   'RAD-MUSY-113','RAD', 1),
    ('Radiographic Technique Applications',        'RAD-TECH-114','RAD', 1),
    ('RAD-B18 (Digital Imaging Systems)',          'RAD-DIG-115', 'RAD', 1),
    ('Radiographic Technique-1',                   'RAD-TECH-211','RAD', 2),
    ('Radiobiology',                               'RAD-RBIO-212','RAD', 2),
    ('Diagnostic Imaging Equipment-1',             'RAD-EQUP-213','RAD', 2),
    ('Patient Care in Imaging',                    'RAD-PTCR-214','RAD', 2),
    ('Imaging Physiology',                         'RAD-PHYS-215','RAD', 2),
    ('RAD-RAD-228 (X-Ray Applications)',           'RAD-RAD-228', 'RAD', 2),
    ('RAD-COMP-314 (Radiological Image Computing)','RAD-COMP-314','RAD', 2),
    ('RAD-ANAT-223 (Radiological Anatomy)',        'RAD-ANAT-223','RAD', 2),
    ('RAD-TECH-224 (Clinical Care Applications)',  'RAD-TECH-224','RAD', 2),
    ('RAD-NUC-315 (Nuclear Medicine & Molecular Imaging)','RAD-NUC-315','RAD', 2),
    ('RAD-RES-227 (Research in Imaging Engineering)','RAD-RES-227','RAD', 2),
    ('RAD-DIS-212 (Radiological Pathology)',       'RAD-DIS-212', 'RAD', 2),
    ('RAD-EQUIP-225 (Calibration & Maintenance)',  'RAD-EQUIP-225','RAD', 2),
    ('MRI (Magnetic Resonance Imaging)',           'RAD-MRI-311', 'RAD', 3),
    ('Radio-Pharmacology',                         'RAD-RPHR-312','RAD', 3),
    ('Chest Radiograph Analysis',                  'RAD-CHRA-313','RAD', 3),
    ('Advanced Imaging Protocols',                 'RAD-AIMP-314','RAD', 3),
    ('Professional Skills (Interventional Radiology)','RAD-PROF-321','RAD', 3),
    ('RAD-CTTEC-326 (CT Scan Technique)',          'RAD-CTTEC-326','RAD', 3),
    ('RAD-SON-325 (Ultrasound Technique)',         'RAD-SON-325', 'RAD', 3),
    ('RAD-MRI-327 (Advanced MRI)',                 'RAD-MRI-327', 'RAD', 3),
    ('RAD-ADTEC-411 (Vascular & Cardiac Imaging)', 'RAD-ADTEC-411','RAD', 3),
    ('Films Review & Interpretation',              'RAD-FILM-411','RAD', 4),
    ('Clerkship Department Rotation',              'RAD-CLRK-412','RAD', 4),
    ('Graduation Project and Seminars',            'RAD-PROJ-413','RAD', 4),

    # ── Medical Laboratory ────────────────────────────────────────────────────
    ('MLS-PHYS-114 (General Lab Physics)',         'MLS-PHYS-114','MLS', 1),
    ('MLS-MATH-128 (Medical Statistics & Mathematics)','MLS-MATH-128','MLS', 1),
    ('MLS-HIST-124 (Histology & Tissue Cells)',    'MLS-HIST-124','MLS', 1),
    ('bbio (Foundation Medical Biology)',          'MLS-BBIO-125','MLS', 1),
    ('MLS-GENE-112 (Introduction to Genetics)',    'MLS-GENE-112','MLS', 1),
    ('MLS-GENE-112B (Molecular Biology Applications)','MLS-GENE-112B','MLS', 1),
    ('MLS-GCHM-113 (Food Chemistry & Metabolism)', 'MLS-GCHM-113','MLS', 1),
    ('MLS-PHYS-122 (Medical Biophysics)',          'MLS-PHYS-122','MLS', 1),
    ('MLS-INTR-212 (Introduction to Medical Analysis)','MLS-INTR-212','MLS', 2),
    ('MLS-IMUN-215 (Clinical Immunology)',         'MLS-IMUN-215','MLS', 2),
    ('MLS-PATH-213 (Histopathology)',              'MLS-PATH-213','MLS', 2),
    ('Protozoology',                               'MLS-PROT-221','MLS', 2),
    ('Medical Entomology and Parasitology',        'MLS-ENTO-222','MLS', 2),
    ('Clinical Microbiology -1',                   'MLS-CMIC-223','MLS', 2),
    ('Basic Microbiology',                         'MLS-BMIC-224','MLS', 2),
    ('Basic Histology & Histological Technique',   'MLS-HIST-225','MLS', 2),
    ('MLS-CCHM-312 (Clinical Chemistry 1)',        'MLS-CCHM-312','MLS', 3),
    ('MLS-HLMT-313 (Clinical Hematology 1)',       'MLS-HLMT-313','MLS', 3),
    ('MLS-CYTO-314 (Clinical Cytology)',           'MLS-CYTO-314','MLS', 3),
    ('Basic Professional Skills-3',                'MLS-PRSK-315','MLS', 3),
    ('MLS-CMIC-315 (Mycology & Virology)',         'MLS-CMIC-315B','MLS', 3),
    ('MLS-SKIL-321 (Practical Skills)',            'MLS-SKIL-321','MLS', 3),
    ('MLS-QUAL-323 (Lab Quality Management)',      'MLS-QUAL-323','MLS', 3),
    ('Molecular Biology Techniques (MBT)',         'MLS-MBT-324', 'MLS', 3),
    ('MLS-MLBT-325 (Molecular Genetic Diagnostics)','MLS-MLBT-325','MLS', 3),
    ('MLS-PUBH-322 (Public Health & Epidemiology)','MLS-PUBH-322','MLS', 3),
    ('MLS-RESH-326 (Introduction to Clinical Research)','MLS-RESH-326','MLS', 3),
    ('Clinical Biochemistry 2',                    'MLS-CCHM-322','MLS', 3),
    ('Laboratory Management & Quality Assurance',  'MLS-MGMT-323','MLS', 3),
    ('VT (Advanced Clinical Lab Training)',        'MLS-VT-411',  'MLS', 4),
    ('MLS-MICR-423 (Advanced Microbiological Diagnosis)','MLS-MICR-423','MLS', 4),
    ('MLS-MICR-424 (Toxicology & Lab Analysis)',   'MLS-MICR-424','MLS', 4),

    # ── Physical Therapy ─────────────────────────────────────────────────────
    ('PT-TERM-217 (PT Terminology)',               'PT-TERM-217', 'PHY', 2),
    ('PT-PEPR-227 (Patient Preparation & Rehab)',  'PT-PEPR-227', 'PHY', 2),
    ('PT-MASS-223 (Massage Therapy Techniques)',   'PT-MASS-223', 'PHY', 2),
    ('PT-KINS-224 (Applied Kinesiology)',          'PT-KINS-224', 'PHY', 2),
    ('Principle of Disease',                       'PT-DISP-221', 'PHY', 2),
    ('Posture and Posture Education',              'PT-POST-222', 'PHY', 2),
    ('Professional Skills -2',                    'PT-PRSK-223', 'PHY', 2),
    ('Gymnastics (Medical & Therapeutic)',         'PT-GYMN-224', 'PHY', 2),
    ('Ergonomics',                                 'PT-ERGO-225', 'PHY', 2),
    ('Therapeutic Exercise',                       'PT-EXER-226', 'PHY', 2),
    ('Biochemistry & Physiology of Exercise',      'PT-BCEX-227', 'PHY', 2),
    ('PT-ICU-324 (PT in Intensive Care)',          'PT-ICU-324',  'PHY', 3),
    ('PT-NEURO-322 (Nervous System Rehabilitation)','PT-NEURO-322','PHY', 3),
    ('PT-PED-323 (Pediatric Physical Therapy)',    'PT-PED-323',  'PHY', 3),
    ('PT-CVRS-325 (Cardiac & Chest Rehabilitation)','PT-CVRS-325','PHY', 3),
    ('Geriatric Care',                             'PT-GERI-326', 'PHY', 3),
    ('Electrotherapy & Heat Modalities',           'PT-ELEC-411', 'PHY', 4),
    ('Training in PT Lab & Electrotherapy',        'PT-TLAB-412', 'PHY', 4),
    ('PT-CASE-423 (Advanced Clinical Cases)',      'PT-CASE-423', 'PHY', 4),

    # ── Computer Science & IT ─────────────────────────────────────────────────
    ('COM-115 (Foundation Computer Science - CS)', 'COM-115-CS',  'CSI', 1),
    ('COM-115 (Foundation Computer Science - IT)', 'COM-115-IT',  'CSI', 1),
    ('COM-126 (Digital Computer Systems)',         'COM-126',     'CSI', 1),
    ('Introduction to Databases',                  'COM-DBIN-127','CSI', 1),
    ('Computer Equipment & Hardware',              'COM-HW-128',  'CSI', 1),
    ('Computer 2 (Structured Programming Languages)','COM-PROG-129','CSI', 1),
    ('Principles of Accounting (CS)',              'COM-ACCT-130','CSI', 1),
    ('Internet Technology INT317 - CS',            'INT317-CS',   'CSI', 3),
    ('Internet Technology INT317 - IT',            'INT317-IT',   'CSI', 3),
    ('Decision Support & Expert Systems - CS',     'COM-DSS-CS',  'CSI', 3),
    ('Decision Support & Expert Systems - IT',     'COM-DSS-IT',  'CSI', 3),
    ('Software Project Management - CS',           'COM-SPM-CS',  'CSI', 3),
    ('Software Project Management - IT',           'COM-SPM-IT',  'CSI', 3),
    ('Operating Systems',                          'COM-OS-211',  'CSI', 2),
    ('Data Structures & Algorithms',               'COM-DSA-212', 'CSI', 2),
    ('Computer Networks',                          'COM-NET-213', 'CSI', 2),
    ('Object Oriented Programming',                'COM-OOP-214', 'CSI', 2),
    ('Database Systems',                           'COM-DBS-215', 'CSI', 2),
    ('Web Development Fundamentals',               'COM-WEB-216', 'CSI', 2),
    ('Systems Analysis & Design I',               'COM-SAD-311', 'CSI', 3),
    ('Artificial Intelligence',                    'COM-AI-312',  'CSI', 3),
    ('Mobile Application Development',             'COM-MOB-313', 'CSI', 3),
    ('Cybersecurity Fundamentals',                 'COM-SEC-314', 'CSI', 3),
    ('Cloud Computing',                            'COM-CLD-315', 'CSI', 3),
    ('Machine Learning',                           'COM-ML-316',  'CSI', 3),
    ('Graduation Project I - CS',                  'COM-PROJ-411','CSI', 4),
    ('Graduation Project II - IT',                 'COM-PROJ-412','CSI', 4),

    # ── Administrative Sciences ───────────────────────────────────────────────
    ('ECON-128 (Macro & Microeconomics)',          'ECON-128',    'ADM', 1),
    ('ACCT-127 (Business Accounting Principles)',  'ACCT-127',    'ADM', 1),
    ('ACCT-316 (Advanced Management & Financial Accounting)','ACCT-316','ADM', 3),
    ('INFO-315 (Strategic Information Systems)',   'INFO-315',    'ADM', 3),
    ('ACCT-312 (Cost Accounting)',                 'ACCT-312',    'ADM', 3),
    ('Productions & Operations Management - MKT', 'ADM-POM-MKT', 'ADM', 3),
    ('Productions & Operations Management - MIS', 'ADM-POM-MIS', 'ADM', 3),
    ('Productions & Operations Management - BA',  'ADM-POM-BA',  'ADM', 3),
    ('Productions & Operations Management - ACCT','ADM-POM-ACCT','ADM', 3),
    ('Business Entrepreneurship - MKT',           'ADM-ENT-MKT', 'ADM', 3),
    ('Business Entrepreneurship - MIS',           'ADM-ENT-MIS', 'ADM', 3),
    ('Business Entrepreneurship - BA',            'ADM-ENT-BA',  'ADM', 3),
    ('Business Entrepreneurship - ACCT',          'ADM-ENT-ACCT','ADM', 3),
    ('Project Management - MKT',                  'ADM-PM-MKT',  'ADM', 3),
    ('Project Management - MIS',                  'ADM-PM-MIS',  'ADM', 3),
    ('Project Management - BA',                   'ADM-PM-BA',   'ADM', 3),
    ('Project Management - ACCT',                 'ADM-PM-ACCT', 'ADM', 3),
    ('Systems Analysis & Design II - MKT',        'INFO-327-MKT','ADM', 3),
    ('Systems Analysis & Design II - MIS',        'INFO-327-MIS','ADM', 3),
    ('Systems Analysis & Design II - BA',         'INFO-327-BA', 'ADM', 3),
    ('Systems Analysis & Design II - ACCT',       'INFO-327-ACCT','ADM', 3),
    ('Research Methodology - MKT',                'ADM-RM-MKT',  'ADM', 3),
    ('Research Methodology - MIS',                'ADM-RM-MIS',  'ADM', 3),
    ('Research Methodology - BA',                 'ADM-RM-BA',   'ADM', 3),
    ('Research Methodology - ACCT',               'ADM-RM-ACCT', 'ADM', 3),
    ('Accounting Information Systems',             'ACCT-AIS-411','ADM', 4),
    ('Financial Management',                       'ADM-FIN-211', 'ADM', 2),
    ('Human Resource Management',                  'ADM-HRM-212', 'ADM', 2),
    ('Marketing Management',                       'ADM-MKT-213', 'ADM', 2),
    ('Business Law',                               'ADM-LAW-214', 'ADM', 2),
    ('Organizational Behavior',                    'ADM-OBH-215', 'ADM', 2),

    # ── Engineering & Architecture ────────────────────────────────────────────
    ('Civil & Electrical General First Year',      'ENG-GFY-111', 'ENG', 1),
    ('ENL-211 (Engineering English 1)',            'ENG-ENL-211', 'ENG', 2),
    ('GEN-211 (Engineering Humanities)',           'ENG-HUM-211', 'ENG', 2),
    ('Structural Analysis I',                      'ENG-STR-212', 'ENG', 2),
    ('Introduction to Civil Engineering',          'ENG-CIVL-213','ENG', 2),
    ('Differential Equations',                     'ENG-DEQN-214','ENG', 2),
    ('MAT221 (Advanced Engineering Mathematics)',  'ENG-MAT-221', 'ENG', 3),
    ('Numerical Methods',                          'ENG-NUM-222', 'ENG', 3),
    ('Computer Aided Design',                      'ENG-CAD-223', 'ENG', 3),
    ('Analog Electronics Circuits',                'ENG-AEC-224', 'ENG', 3),
    ('Control Theory',                             'ENG-CTR-225', 'ENG', 3),
    ('Electromagnetic Fields Theory',              'ENG-EMF-226', 'ENG', 3),
    ('Elements of Power Systems',                  'ENG-PWR-227', 'ENG', 3),
    ('Electrochemical Conversions',                'ENG-ECH-228', 'ENG', 3),
    ('GEN-421 (Shared General Course)',            'ENG-GEN-421', 'ENG', 4),
    ('GEN-422 (Project & Economic Management)',    'ENG-GEN-422', 'ENG', 4),
    ('Fluid Mechanics',                            'ENG-FLMD-311','ENG', 3),
    ('Soil Mechanics',                             'ENG-SOIL-312','ENG', 3),
    ('Concrete Technology',                        'ENG-CONC-313','ENG', 3),
    ('Surveying Engineering',                      'ENG-SURV-211','ENG', 2),
    ('Engineering Drawing',                        'ENG-DRAW-111','ENG', 1),
    ('Engineering Mathematics 1',                  'ENG-MATH-111','ENG', 1),

    # ── Nursing ───────────────────────────────────────────────────────────────
    ('Fundamentals of Nursing 1',                  'NUR-FUND-111','NUR', 1),
    ('HBSF (Human Body Structure & Functions 1)',  'NUR-HBSF-112','NUR', 1),
    ('History & Ethics of Nursing',                'NUR-ETH-113', 'NUR', 1),
    ('Medical Terminology Nursing',                'NUR-TERM-114','NUR', 1),
    ('NUR-ANAT-124 (Applied Anatomy)',             'NUR-ANAT-124','NUR', 1),
    ('NURMICRO-122 (Clinical Microbiology)',       'NUR-MICR-122','NUR', 1),
    ('NUR-BIOCH-123 (Biochemistry)',               'NUR-BIOC-123','NUR', 1),
    ('Community Health Nursing 1',                 'NUR-CHN-124', 'NUR', 1),
    ('Human Body Structure and Function 2',        'NUR-HBSF-125','NUR', 1),
    ('Fundamentals of Nursing-2',                  'NUR-FUND-126','NUR', 1),
    ('Surgical Nursing',                           'NUR-SURG-211','NUR', 2),
    ('Medical Nursing',                            'NUR-MEDN-212','NUR', 2),
    ('Nutrition (Nursing)',                        'NUR-NUTR-213','NUR', 2),
    ('Basic Therapeutics (Pharmacology)',           'NUR-PHAR-214','NUR', 2),
    ('English 3 (Nursing)',                        'NUR-ENGL-215','NUR', 2),
    ('NUR-EDU-221 (Nursing Education Methods)',    'NUR-EDU-221', 'NUR', 2),
    ('NUR-SOCIO-222 (Medical Sociology)',          'NUR-SOCIO-222','NUR', 2),
    ('NUR-COUN-223 (Psychological Counseling)',    'NUR-COUN-223','NUR', 2),
    ('NUR-MED-224 (Critical Medical Cases)',       'NUR-MED-224', 'NUR', 2),
    ('NUR-SURG-225 (Surgical Cases & Operations)', 'NUR-SURG-225','NUR', 2),
    ('NUR-THEO (Modern Nursing Theories)',         'NUR-THEO-321','NUR', 3),
    ('Biostatistics Nurse',                        'NUR-BIOS-322','NUR', 3),
    ('Advanced Clinical Care Applications',        'NUR-CLIN-323','NUR', 3),
    ('NUR-THEO-322 (Nursing Practice Management)', 'NUR-MGMT-322','NUR', 3),
    ('NUR-CHC-323 (Maternal & Child Health)',      'NUR-CHC-323', 'NUR', 3),
    ('NUR-PED-324 (Neonatal & Pediatric Nursing)', 'NUR-PED-324', 'NUR', 3),
    ('NUR-PSYC-325 (Psychiatric Nursing)',         'NUR-PSYC-325','NUR', 3),
    ('NUR-REC-326 (Nursing Research Methods)',     'NUR-REC-326', 'NUR', 3),

    # ── International Relations & Diplomatic Studies ───────────────────────────
    ('pct (Political Concepts & Terminologies)',   'IRD-PCT-111', 'IRD', 1),
    ('Political Concepts & Terminologies 1',       'IRD-POL-112', 'IRD', 1),
    ('Introduction to Political Science',          'IRD-IPS-113', 'IRD', 1),
    ('Introduction to Sociology',                  'IRD-SOC-114', 'IRD', 1),
    ('Arabic Language-IRDS',                       'IRD-ARAB-115','IRD', 1),
    ('French Language (IR)',                        'IRD-FRN-116', 'IRD', 1),
    ('IRD-ECOP-116 (International Political Economy)','IRD-ECOP-116','IRD', 1),
    ('Introduction to Modern Diplomacy',           'IRD-DIP-211', 'IRD', 2),
    ('International Politics & Security',          'IRD-IPS-212', 'IRD', 2),
    ('Public Policy, Processes & Strategies',      'IRD-PPP-213', 'IRD', 2),
    ('Spanish Language',                           'IRD-SPN-221', 'IRD', 2),
    ('French Language 4',                          'IRD-FRN-222', 'IRD', 2),
    ('Chinese Language',                           'IRD-CHN-223', 'IRD', 2),
    ('Strategic Geography and Geopolitics',        'IRD-GEO-224', 'IRD', 2),
    ('Politics & Government in Sudan',             'IRD-PGS-225', 'IRD', 2),
    ('International Economic Relations',           'IRD-IER-226', 'IRD', 2),
    ('Foreign Policy Analysis',                    'IRD-FPA-227', 'IRD', 2),
    ('International Law',                          'IRD-LAW-228', 'IRD', 2),
    ('French Language 6 - IR',                     'IRD-FRN-IR-311','IRD', 3),
    ('French Language 6 - DS',                     'IRD-FRN-DS-311','IRD', 3),
    ('Chinese Language 6 - IR',                    'IRD-CHN-IR-312','IRD', 3),
    ('Chinese Language 6 - DS',                    'IRD-CHN-DS-312','IRD', 3),
    ('Spanish Language 6 - IR',                    'IRD-SPN-IR-313','IRD', 3),
    ('Spanish Language 6 - DS',                    'IRD-SPN-DS-313','IRD', 3),
    ('English Language 6 - IR',                    'IRD-ENG-IR-314','IRD', 3),
    ('English Language 6 - DS',                    'IRD-ENG-DS-314','IRD', 3),
    ('International Environmental Politics - IR',  'IRD-IEP-IR-315','IRD', 3),
    ('International Environmental Politics - DS',  'IRD-IEP-DS-315','IRD', 3),
    ('Global Governance and Diplomacy - IR',       'IRD-GGD-IR-316','IRD', 3),
    ('Global Governance and Diplomacy - DS',       'IRD-GGD-DS-316','IRD', 3),
    ('Human Rights Law',                           'IRD-HRL-311', 'IRD', 3),
    ('African Politics',                           'IRD-AFP-312', 'IRD', 3),
    ('Conflict Resolution & Peacebuilding',        'IRD-CRP-411', 'IRD', 4),
    ('International Organizations',                'IRD-IOR-412', 'IRD', 4),
]

# Additional courses to reach 887 total
EXTRA_COURSES_TEMPLATE = [
    # MED extras
    ('Dermatology (Medicine)', 'MED', 3), ('Neurology', 'MED', 4),
    ('Cardiology', 'MED', 4), ('Gastroenterology', 'MED', 4),
    ('Urology', 'MED', 4), ('Orthopedics (Medicine)', 'MED', 4),
    ('Radiology for Medicine', 'MED', 3), ('Immunology', 'MED', 3),
    ('Clinical Microbiology (Medicine)', 'MED', 3), ('Neonatology', 'MED', 5),
    ('Geriatrics', 'MED', 5), ('Hematology', 'MED', 4),
    ('Oncology', 'MED', 5), ('Rheumatology', 'MED', 4),
    ('Tropical Medicine Advanced', 'MED', 5), ('Physical Examination Skills', 'MED', 2),
    ('Medical Imaging for Clinicians', 'MED', 3), ('Patient Safety', 'MED', 2),
    ('Endocrine Disorders', 'MED', 4), ('Infectious Disease', 'MED', 4),
    # PHA extras
    ('Clinical Toxicology', 'PHA', 4), ('Hospital Pharmacy', 'PHA', 4),
    ('Regulatory Affairs', 'PHA', 5), ('Drug Information', 'PHA', 4),
    ('Pharmaceutical Care', 'PHA', 5), ('Sterile Manufacturing', 'PHA', 4),
    ('Pharmacovigilance', 'PHA', 5), ('Herbal Medicine', 'PHA', 3),
    # DEN extras
    ('Conservative Dentistry-2', 'DEN', 4), ('Prosthodontics-3', 'DEN', 4),
    ('Pedodontics Advanced', 'DEN', 4), ('Periodontics-2', 'DEN', 4),
    ('Dental Implantology', 'DEN', 4), ('Oral Radiology', 'DEN', 3),
    ('Special Needs Dentistry', 'DEN', 4), ('Dental Audit', 'DEN', 4),
    # RAD extras
    ('Advanced CT Techniques', 'RAD', 4), ('Mammography', 'RAD', 4),
    ('Fluoroscopy', 'RAD', 3), ('Radiation Safety & Protection', 'RAD', 2),
    ('Emergency Radiology', 'RAD', 4), ('Paediatric Radiology', 'RAD', 4),
    # MLS extras
    ('Virology', 'MLS', 3), ('Haematology 2', 'MLS', 4),
    ('Clinical Chemistry 3', 'MLS', 4), ('Serology & Immunoserology', 'MLS', 3),
    ('Blood Banking & Transfusion', 'MLS', 4), ('Point of Care Testing', 'MLS', 4),
    ('Lab Informatics', 'MLS', 3), ('Mycobacteriology', 'MLS', 3),
    # PHY extras
    ('Sports Rehabilitation', 'PHY', 3), ('Aquatic Therapy', 'PHY', 3),
    ('Manual Therapy', 'PHY', 3), ('Occupational Therapy Intro', 'PHY', 2),
    ('Prosthetics & Orthotics', 'PHY', 3), ('Wound Care & Burns', 'PHY', 4),
    # CSI extras
    ('Software Engineering', 'CSI', 3), ('Compiler Design', 'CSI', 3),
    ('Computer Architecture', 'CSI', 2), ('Discrete Mathematics', 'CSI', 1),
    ('Digital Logic Design', 'CSI', 1), ('Theory of Computation', 'CSI', 3),
    ('Data Mining', 'CSI', 4), ('Big Data Analytics', 'CSI', 4),
    ('IoT Systems', 'CSI', 4), ('Blockchain Fundamentals', 'CSI', 4),
    ('DevOps Practices', 'CSI', 4), ('Network Security', 'CSI', 3),
    ('Virtual Reality & AR', 'CSI', 4), ('Game Development', 'CSI', 4),
    # ADM extras
    ('Supply Chain Management', 'ADM', 3), ('E-Commerce', 'ADM', 3),
    ('Corporate Governance', 'ADM', 4), ('International Business', 'ADM', 3),
    ('Operations Research', 'ADM', 3), ('Digital Marketing', 'ADM', 4),
    ('Taxation', 'ADM', 3), ('Auditing', 'ADM', 4),
    ('Investment Analysis', 'ADM', 4), ('Insurance & Risk Management', 'ADM', 4),
    ('Financial Reporting', 'ADM', 3), ('Bank Management', 'ADM', 4),
    # ENG extras
    ('Transportation Engineering', 'ENG', 3), ('Environmental Engineering', 'ENG', 3),
    ('Structural Design', 'ENG', 4), ('Geotechnical Engineering', 'ENG', 3),
    ('Construction Management', 'ENG', 4), ('Electrical Machines', 'ENG', 3),
    ('Power Electronics', 'ENG', 4), ('Telecommunications', 'ENG', 3),
    ('Digital Signal Processing', 'ENG', 4), ('Renewable Energy Systems', 'ENG', 4),
    ('Architecture Design Studio 1', 'ENG', 2), ('Architecture Design Studio 2', 'ENG', 3),
    ('Urban Planning', 'ENG', 4), ('Building Materials', 'ENG', 2),
    ('Sanitary Engineering', 'ENG', 3), ('Highway Engineering', 'ENG', 3),
    # NUR extras
    ('Critical Care Nursing', 'NUR', 3), ('Emergency Nursing', 'NUR', 3),
    ('Operating Room Nursing', 'NUR', 3), ('Oncology Nursing', 'NUR', 4),
    ('Dialysis Nursing', 'NUR', 4), ('Mental Health Nursing', 'NUR', 3),
    ('Gerontological Nursing', 'NUR', 4), ('Transcultural Nursing', 'NUR', 3),
    # IRD extras
    ('Middle East Politics', 'IRD', 3), ('African Union & Regional Organizations', 'IRD', 3),
    ('Humanitarian Law', 'IRD', 4), ('Diplomatic Protocol', 'IRD', 3),
    ('UN System & Global Governance', 'IRD', 2), ('Migration & Refugee Studies', 'IRD', 4),
    ('Security Studies', 'IRD', 3), ('Political Economy of Development', 'IRD', 4),
]

# ──────────────────────────────────────────────────────────────────────────────
# NAMES for random data generation
# ──────────────────────────────────────────────────────────────────────────────
MALE_FIRST = [
    'أحمد','محمد','عمر','يوسف','علي','إبراهيم','خالد','مصطفى','عبدالله','حسن',
    'حسين','طارق','سامي','وليد','نور','ياسر','بلال','أنس','زياد','فيصل',
    'عادل','نادر','كريم','رامي','تامر','هشام','عصام','صلاح','رضا','جمال',
    'عمرو','مجدي','سعد','منصور','ماهر','نبيل','ناصر','شريف','ربيع','سيف',
]
FEMALE_FIRST = [
    'فاطمة','مريم','زينب','سارة','نور','هدى','رنا','سلمى','دينا','إيمان',
    'نادية','منال','أسماء','ريم','لينا','هبة','دعاء','أميرة','نيلى','شيماء',
    'لمياء','ربى','رنيم','مها','وفاء','رشا','سمية','إلهام','نهاد','وداد',
]
LAST_NAMES = [
    'محمد','أحمد','عبدالله','عبدالرحمن','إبراهيم','حسن','علي','عمر','حسين','المختار',
    'الأمين','عوض','عثمان','يوسف','آدم','صالح','داود','موسى','عيسى','إسماعيل',
    'طاهر','نور','الحاج','الشيخ','خليل','جبريل','سليمان','دريج','بابكر','خضر',
    'تيجاني','مكاوي','الجزولي','البشير','ميرغني','القرشي','ودعة','محجوب','الزين','البدوي',
    'النور','الفاتح','الأمير','الرشيد','منصور','شقلاوي','فرح','مدني','الشافعي','رحمة',
]
DEGREES = ['BSc', 'MSc', 'PhD', 'Prof']
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
BATCHES = ['2021', '2022', '2023', '2024', '2025']


def rand_name(gender='M'):
    first = random.choice(MALE_FIRST if gender == 'M' else FEMALE_FIRST)
    last  = random.choice(LAST_NAMES)
    return f'{first} {last}'


def rand_phone():
    return '09' + str(random.randint(10000000, 99999999))


# ──────────────────────────────────────────────────────────────────────────────
class Command(BaseCommand):
    help = 'Seed NUSU production data into the VPS database'

    def add_arguments(self, parser):
        parser.add_argument('--fresh', action='store_true',
                            help='Wipe all seeded data before re-seeding')

    def handle(self, *args, **options):
        if options['fresh']:
            self.stdout.write(self.style.WARNING('⚠ Clearing existing data...'))
            Student.objects.all().delete()
            Teacher.objects.all().delete()
            Coordinator.objects.all().delete()
            Course.objects.all().delete()
            Department.objects.all().delete()
            College.objects.all().delete()
            User.objects.filter(username__startswith='gf').delete()
            User.objects.filter(username__startswith='tf').delete()
            User.objects.filter(username__startswith='sf').delete()

        # ── 1. Colleges ────────────────────────────────────────────────────
        self.stdout.write('Creating colleges...')
        college_map = {}   # code → College instance
        for code, arabic, english in COLLEGES:
            col, _ = College.objects.get_or_create(
                college_name=arabic,
                defaults={'name': english}
            )
            college_map[code] = col
        self.stdout.write(self.style.SUCCESS(f'  OK {len(college_map)} colleges'))

        # ── 2. Departments ─────────────────────────────────────────────────
        self.stdout.write('Creating departments...')
        dept_map = {}   # (college_code, dept_name) → Department
        for code, dept_names in DEPARTMENTS.items():
            col = college_map[code]
            for dname in dept_names:
                dept, _ = Department.objects.get_or_create(
                    name=dname, college=col
                )
                dept_map[(code, dname)] = dept
        self.stdout.write(self.style.SUCCESS(f'  OK departments created'))

        # ── 3. Courses from document ───────────────────────────────────────
        self.stdout.write('Creating courses from document...')
        created_codes = set(Course.objects.values_list('course_code', flat=True))
        course_count  = 0
        for title, code, c_code, yr in DOC_COURSES:
            if code in created_codes:
                continue
            col  = college_map.get(c_code)
            depts = list(Department.objects.filter(college=col))
            dept = depts[0] if depts else None
            Course.objects.create(
                course_code=code, title=title,
                credits=3, total_hours=3,
                college=col, department=dept, year_level=yr
            )
            created_codes.add(code)
            course_count += 1

        # ── 4. Extra courses to reach 887 ──────────────────────────────────
        self.stdout.write('Generating extra courses to reach 887...')
        idx = 1
        for title, c_code, yr in EXTRA_COURSES_TEMPLATE:
            if len(created_codes) >= 887:
                break
            while True:
                code = f'{c_code}-EX-{idx:04d}'
                if code not in created_codes:
                    break
                idx += 1
            col   = college_map.get(c_code)
            depts = list(Department.objects.filter(college=col))
            dept  = depts[0] if depts else None
            Course.objects.get_or_create(
                course_code=code,
                defaults=dict(title=title, credits=3, total_hours=3,
                              college=col, department=dept, year_level=yr)
            )
            created_codes.add(code)
            idx += 1

        # Fill remaining to 887
        college_codes = list(college_map.keys())
        years = [1, 2, 3, 4]
        extra_titles = [
            'Advanced Topics in {}', '{} Seminar', 'Special Topics: {}',
            'Research in {}', 'Applied {}', '{} Lab', 'Introduction to {}',
            'Principles of {}', 'Clinical {}', 'Advanced {}'
        ]
        subjects = [
            'Biochemistry', 'Genetics', 'Pathology', 'Pharmacology', 'Anatomy',
            'Physiology', 'Statistics', 'Ethics', 'Communication', 'Research Methods',
            'Data Science', 'Systems', 'Management', 'Economics', 'Mathematics',
            'Engineering', 'Technology', 'Nursing Care', 'Clinical Practice',
        ]
        while len(created_codes) < 887:
            c_code = random.choice(college_codes)
            yr     = random.choice(years)
            subj   = random.choice(subjects)
            tmpl   = random.choice(extra_titles)
            title  = tmpl.format(subj)
            code   = f'{c_code}-FILL-{idx:04d}'
            idx   += 1
            if code in created_codes:
                continue
            col   = college_map.get(c_code)
            depts = list(Department.objects.filter(college=col))
            dept  = depts[0] if depts else None
            Course.objects.get_or_create(
                course_code=code,
                defaults=dict(title=title, credits=3, total_hours=3,
                              college=col, department=dept, year_level=yr)
            )
            created_codes.add(code)

        total_courses = Course.objects.count()
        self.stdout.write(self.style.SUCCESS(f'  OK {total_courses} courses total'))

        # ── 5. ONE Gate user ───────────────────────────────────────────────
        # gf1-15, tf1-3, sf1-3 are CLASSROOM/DEPARTMENT devices, not user accounts.
        # Only the physical gate needs a login.
        self.stdout.write('Creating gate login user...')
        if not User.objects.filter(username='gate').exists():
            User.objects.create_user(
                username='gate',
                email='gate@nusu.edu.sd',
                password=GATE_PWD,
                first_name='Gate', last_name='Security'
            )
        self.stdout.write(self.style.SUCCESS('  OK gate user created (username=gate)'))

        # ── 6. Teachers (399 total) ─────────────────────────────────────────
        self.stdout.write('Creating 399 teachers...')
        colleges_list = list(college_map.values())
        existing_teachers = Teacher.objects.count()
        needed_teachers   = max(0, 399 - existing_teachers)

        # All teachers are plain records — no linked auth users
        for _ in range(needed_teachers):
            gender = random.choice(['M', 'F'])
            col    = random.choice(colleges_list)
            depts  = list(Department.objects.filter(college=col))
            dept   = depts[0] if depts else None
            Teacher.objects.create(
                name=rand_name(gender), gender=gender,
                academic_degree=random.choice(DEGREES),
                college=col, department=dept,
                university_email=f'staff{uuid.uuid4().hex[:8]}@nusu.edu.sd',
                phone_number=rand_phone()
            )
        self.stdout.write(self.style.SUCCESS(f'  OK {Teacher.objects.count()} teachers total'))

        # ── 7. Students (9889 total) ────────────────────────────────────────
        self.stdout.write('Creating 9889 students (this may take a minute)...')
        existing_students = Student.objects.count()
        needed_students   = max(0, 9889 - existing_students)

        all_depts = list(Department.objects.all())

        # Bulk create remaining students for performance
        CHUNK = 500
        created_so_far = Student.objects.count()
        batch_objs = []
        used_codes  = set(Student.objects.values_list('student_code', flat=True))

        for i in range(needed_students):
            gender = random.choice(['M', 'F'])
            dept   = random.choice(all_depts) if all_depts else None
            while True:
                code = f'NU-{random.randint(10000, 99999)}'
                if code not in used_codes:
                    used_codes.add(code)
                    break
            batch_objs.append(Student(
                student_code=code,
                name=rand_name(gender),
                department=dept,
                university_email=f's{code.replace("NU-", "")}@nusu.edu.sd',
                phone_number=rand_phone(),
                batch=random.choice(BATCHES),
                is_registered=random.choice([True, False]),
                is_allowed_entry=True,
            ))
            if len(batch_objs) >= CHUNK:
                Student.objects.bulk_create(batch_objs, ignore_conflicts=True)
                batch_objs = []
                self.stdout.write(f'    … {Student.objects.count()} students created', ending='\r')
                self.stdout.flush()

        if batch_objs:
            Student.objects.bulk_create(batch_objs, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'\n  OK {Student.objects.count()} students total'))

        # ── 8. Coordinators (1 per college) ───────────────────────────────
        self.stdout.write('Creating coordinators...')
        for i, (code, arabic, english) in enumerate(COLLEGES):
            uname = f'coord_{code.lower()}'
            col   = college_map[code]
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(
                    username=uname,
                    email=f'coord_{code.lower()}@nusu.edu.sd',
                    password=COORD_PWD,
                    is_staff=True
                )
                Coordinator.objects.get_or_create(
                    auth_user=u,
                    defaults=dict(
                        name=rand_name('F'),
                        college=col,
                        university_email=u.email,
                        phone_number=rand_phone()
                    )
                )
        self.stdout.write(self.style.SUCCESS('  OK coordinators created'))

        # ── Summary ────────────────────────────────────────────────────────
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
        self.stdout.write(f'  Colleges    : {College.objects.count()}')
        self.stdout.write(f'  Departments : {Department.objects.count()}')
        self.stdout.write(f'  Courses     : {Course.objects.count()}')
        self.stdout.write(f'  Teachers    : {Teacher.objects.count()}')
        self.stdout.write(f'  Students    : {Student.objects.count()}')
        self.stdout.write(f'  Gate login  : gate      | pwd: {GATE_PWD}')
        self.stdout.write(f'  NOTE: gf1-15/tf1-3/sf1-3 are classroom devices, not user accounts')
        self.stdout.write(f'  Coordinators: coord_gen, coord_med … | pwd: {COORD_PWD}')
        self.stdout.write('=' * 50)
