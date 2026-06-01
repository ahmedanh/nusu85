# -*- coding: utf-8 -*-
"""
Re-encode every enrolled face image with the ACTIVE face engine
(settings.FACE_ENGINE) and store the resulting embedding.

Use this after switching FACE_ENGINE (e.g. dlib → insightface) because
the two engines produce different-dimension vectors (128 vs 512).

    python manage.py reenroll_faces                # both students + teachers
    python manage.py reenroll_faces --only students
    python manage.py reenroll_faces --dry-run

Safe by design: only rows whose face image can be re-encoded are updated;
the matcher ignores any leftover mismatched-dimension vectors, so a partial
run never produces false matches.
"""
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Re-encode enrolled faces with the active FACE_ENGINE.'

    def add_arguments(self, parser):
        parser.add_argument('--only', choices=['students', 'teachers'], default=None)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        from attendance import face_engine as fe
        from attendance.models import (
            Student, Teacher, StudentFaceEmbedding, TeacherFaceEmbedding,
        )
        try:
            import face_recognition
        except Exception:
            face_recognition = None

        engine = fe.active_engine()
        self.stdout.write(self.style.NOTICE(
            f'Active engine: {engine} ({fe.embedding_dim()}-dim) '
            f'| available={fe.available()}'))
        if not fe.available():
            self.stderr.write(self.style.ERROR('Engine not available — aborting.'))
            return

        dry = opts['dry_run']
        only = opts['only']
        done = {'students': 0, 'teachers': 0, 'skipped': 0}

        def _img(path):
            if face_recognition is not None:
                return face_recognition.load_image_file(path)
            from PIL import Image
            import numpy as np
            return np.array(Image.open(path).convert('RGB'))

        if only in (None, 'students'):
            for s in Student.objects.exclude(face_image='').exclude(face_image__isnull=True):
                try:
                    emb = fe.encode(_img(s.face_image.path))
                except Exception:
                    emb = None
                if not emb:
                    done['skipped'] += 1
                    continue
                if not dry:
                    StudentFaceEmbedding.objects.update_or_create(
                        student=s, defaults={'embedding': emb})
                done['students'] += 1
                self.stdout.write(f'  ✓ student {s.pk} {getattr(s, "name", "")[:20]}')

        if only in (None, 'teachers'):
            for t in Teacher.objects.exclude(face_image='').exclude(face_image__isnull=True):
                try:
                    emb = fe.encode(_img(t.face_image.path))
                except Exception:
                    emb = None
                if not emb:
                    done['skipped'] += 1
                    continue
                if not dry:
                    TeacherFaceEmbedding.objects.update_or_create(
                        teacher=t, defaults={'face_vector': emb})
                done['teachers'] += 1
                self.stdout.write(f'  ✓ teacher {t.pk} {getattr(t, "name", "")[:20]}')

        verb = 'WOULD re-enroll' if dry else 're-enrolled'
        self.stdout.write(self.style.SUCCESS(
            f'{verb}: {done["students"]} students, {done["teachers"]} teachers '
            f'(skipped {done["skipped"]} with no detectable face)'))
