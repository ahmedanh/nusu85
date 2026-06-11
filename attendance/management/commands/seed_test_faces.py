"""
Management command: seed_test_faces
====================================
Enrolls a face photo for all test demo accounts so that face recognition
works immediately without manual camera enrollment.

Usage:
    # Enroll YOUR photo for all test accounts:
    python manage.py seed_test_faces --photo path/to/photo.jpg

    # Enroll for specific user type only:
    python manage.py seed_test_faces --photo photo.jpg --type student
    python manage.py seed_test_faces --photo photo.jpg --type teacher

    # Enroll for a specific username:
    python manage.py seed_test_faces --photo photo.jpg --username test_student

    # List test accounts in DB:
    python manage.py seed_test_faces --list

Notes:
    - Works with both dlib (128-dim) and insightface (512-dim) engines
    - USE_LOCAL_DB=true → writes to SQLite, otherwise PostgreSQL
    - Run again to overwrite existing embeddings
"""

import os
import sys
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from attendance.models import Student, Teacher, StudentFaceEmbedding, TeacherFaceEmbedding
import attendance.face_engine as _fe


TEST_USERNAMES = [
    'test_student', 'test_student2',
    'test_teacher', 'test_teacher2',
    'test_admin', 'test_coordinator', 'test_gate',
]


class Command(BaseCommand):
    help = 'Enroll a face photo for demo/test accounts — fixes zero-embedding recognition failure'

    def add_arguments(self, parser):
        parser.add_argument('--photo', '-p', type=str, default=None,
                            help='Path to JPG/PNG photo file to use as face embedding source')
        parser.add_argument('--username', '-u', type=str, default=None,
                            help='Specific username to enroll (default: all test accounts)')
        parser.add_argument('--type', '-t', choices=['student', 'teacher', 'all'],
                            default='all', help='Enroll students, teachers, or all (default: all)')
        parser.add_argument('--list', '-l', action='store_true',
                            help='List all test accounts and their enrollment status')
        parser.add_argument('--clear', action='store_true',
                            help='Clear all face embeddings (dangerous! use with caution)')

    def handle(self, *args, **options):
        if options['list']:
            self._list_accounts()
            return

        if options['clear']:
            confirm = input('⚠️  Clear ALL face embeddings? Type YES to confirm: ')
            if confirm.strip() == 'YES':
                StudentFaceEmbedding.objects.all().delete()
                TeacherFaceEmbedding.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Cleared all face embeddings.'))
            else:
                self.stdout.write('Cancelled.')
            return

        photo_path = options['photo']
        if not photo_path:
            # Try auto-detect common locations
            candidates = [
                'test_face.jpg', 'face.jpg', 'photo.jpg',
                'test_face.png', 'face.png',
                os.path.expanduser('~/Downloads/face.jpg'),
                os.path.expanduser('~/Pictures/face.jpg'),
            ]
            for c in candidates:
                if os.path.exists(c):
                    photo_path = c
                    self.stdout.write(f'Auto-detected photo: {c}')
                    break

        if not photo_path:
            raise CommandError(
                'No photo specified.\n'
                'Usage: python manage.py seed_test_faces --photo path/to/photo.jpg\n\n'
                'Place a clear face photo at the project root named "test_face.jpg" for auto-detection.'
            )

        if not os.path.exists(photo_path):
            raise CommandError(f'Photo not found: {photo_path}')

        # Load and encode the photo
        self.stdout.write(f'Loading photo: {photo_path}')
        try:
            import cv2
            img = cv2.imread(photo_path)
            if img is None:
                raise CommandError(f'Cannot read image file: {photo_path}')
            img_rgb = img[:, :, ::-1]  # BGR → RGB
        except ImportError:
            raise CommandError('OpenCV (cv2) not installed. Run: pip install opencv-python-headless')

        # Check engine availability
        engine = _fe.active_engine()
        self.stdout.write(f'Face engine: {engine} ({_fe.embedding_dim()}-dim)')

        if not _fe.available():
            raise CommandError(
                f'Face engine "{engine}" is not available.\n'
                'For insightface: pip install insightface onnxruntime\n'
                'For dlib: pip install face_recognition'
            )

        # Encode the face
        self.stdout.write('Detecting and encoding face...')
        embedding = _fe.encode(img_rgb)
        if embedding is None:
            raise CommandError(
                'No face detected in the photo.\n'
                'Tips:\n'
                '  - Use a clear front-facing photo\n'
                '  - Good lighting, no mask\n'
                '  - Face should be the main subject\n'
                '  - Try a different photo'
            )

        dim = len(embedding)
        self.stdout.write(self.style.SUCCESS(f'✓ Face detected — {dim}-dim embedding extracted'))

        # Also generate 4 synthetic "extra angle" embeddings by adding small noise
        # These simulate multi-angle enrollment so matching is more robust
        extra_embeddings = []
        emb_arr = np.array(embedding, dtype=np.float32)
        for i in range(4):
            noise = np.random.normal(0, 0.02, emb_arr.shape).astype(np.float32)
            noisy = emb_arr + noise
            # Re-normalize (insightface expects L2-normalised vectors)
            norm = np.linalg.norm(noisy)
            if norm > 0:
                noisy = noisy / norm
            extra_embeddings.append(noisy.tolist())

        self.stdout.write(f'✓ Generated {len(extra_embeddings)} extra angle embeddings (noise-augmented)')

        # Determine who to enroll
        target_username = options['username']
        enroll_type = options['type']

        enrolled_students = 0
        enrolled_teachers = 0
        skipped = 0

        if target_username:
            # Specific username
            try:
                user = User.objects.get(username=target_username)
            except User.DoesNotExist:
                raise CommandError(f'User not found: {target_username}')
            s = Student.objects.filter(auth_user=user).first()
            t = Teacher.objects.filter(auth_user=user).first()
            if s:
                self._enroll_student(s, embedding, extra_embeddings)
                enrolled_students += 1
            elif t:
                self._enroll_teacher(t, embedding, extra_embeddings)
                enrolled_teachers += 1
            else:
                self.stdout.write(self.style.WARNING(f'  {target_username}: not linked to student/teacher'))
                skipped += 1
        else:
            # All test accounts
            usernames = TEST_USERNAMES
            for uname in usernames:
                try:
                    user = User.objects.get(username=uname)
                except User.DoesNotExist:
                    self.stdout.write(f'  {uname}: not found in DB, skipping')
                    skipped += 1
                    continue

                s = Student.objects.filter(auth_user=user).first()
                t = Teacher.objects.filter(auth_user=user).first()

                if s and enroll_type in ('student', 'all'):
                    self._enroll_student(s, embedding, extra_embeddings)
                    enrolled_students += 1
                elif t and enroll_type in ('teacher', 'all'):
                    self._enroll_teacher(t, embedding, extra_embeddings)
                    enrolled_teachers += 1
                else:
                    self.stdout.write(f'  {uname}: no student/teacher profile, skipping')
                    skipped += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✅ Done! Students: {enrolled_students}, Teachers: {enrolled_teachers}, Skipped: {skipped}'
        ))
        self.stdout.write(
            'Face recognition is now enabled for the enrolled accounts.\n'
            'Test at: /attendance/scan/ or /attendance/gate/'
        )

    def _enroll_student(self, student, embedding, extras):
        obj, created = StudentFaceEmbedding.objects.get_or_create(
            student=student,
            defaults={'embedding': embedding, 'extra_embeddings': extras}
        )
        if not created:
            obj.embedding = embedding
            obj.extra_embeddings = extras
            obj.save()
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  ✓ [Student] {student.name}: {action}')

    def _enroll_teacher(self, teacher, embedding, extras):
        obj, created = TeacherFaceEmbedding.objects.get_or_create(
            teacher=teacher,
            defaults={'face_vector': embedding, 'extra_embeddings': extras}
        )
        if not created:
            obj.face_vector = embedding
            obj.extra_embeddings = extras
            obj.save()
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'  ✓ [Teacher] {teacher.name}: {action}')

    def _list_accounts(self):
        self.stdout.write('\n=== Test Accounts & Face Enrollment Status ===\n')
        for uname in TEST_USERNAMES:
            try:
                user = User.objects.get(username=uname)
            except User.DoesNotExist:
                self.stdout.write(f'  ✗ {uname}: NOT IN DB')
                continue

            s = Student.objects.filter(auth_user=user).first()
            t = Teacher.objects.filter(auth_user=user).first()

            if s:
                has_emb = StudentFaceEmbedding.objects.filter(student=s).exists()
                emb = StudentFaceEmbedding.objects.filter(student=s).first()
                extras = len(emb.extra_embeddings) if emb else 0
                status = f'✓ ENROLLED ({extras} extra angles)' if has_emb else '✗ NOT ENROLLED'
                self.stdout.write(f'  [Student] {uname} → {s.name}: {status}')
            elif t:
                has_emb = TeacherFaceEmbedding.objects.filter(teacher=t).exists()
                emb = TeacherFaceEmbedding.objects.filter(teacher=t).first()
                extras = len(emb.extra_embeddings) if emb else 0
                status = f'✓ ENROLLED ({extras} extra angles)' if has_emb else '✗ NOT ENROLLED'
                self.stdout.write(f'  [Teacher] {uname} → {t.name}: {status}')
            else:
                self.stdout.write(f'  [?] {uname}: no student/teacher profile linked')

        total_s = StudentFaceEmbedding.objects.count()
        total_t = TeacherFaceEmbedding.objects.count()
        self.stdout.write(f'\nTotal enrolled — Students: {total_s}, Teachers: {total_t}')
