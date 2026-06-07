from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY    = config('SECRET_KEY')
DEPLOY_SECRET = config('DEPLOY_SECRET', default='')   # set on VPS for live-reload push
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,84.46.251.93,shamel.sd,www.shamel.sd,10.0.2.2').split(',')

# CSRF trusted origins — cover all ports used locally + production domain
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:9000',
    'http://localhost:8000',
    'http://localhost:9000',
    'https://shamel.sd',
    'https://www.shamel.sd',
    'http://84.46.251.93',
    'http://10.0.2.2:8000',
    'http://10.0.2.2:9000',
]

# ─────────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'axes',
    'attendance',
]

# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
MIDDLEWARE = [
    'attendance.middleware.CloseOldConnectionsMiddleware',  # must be first — fixes stale VPS connections
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'acdc_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'attendance' / 'templates' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'attendance.context_processors.notifications_processor',
            ],
            'libraries': {
                'custom_filters': 'attendance.templatetags.custom_filters',
            },
        },
    },
]

WSGI_APPLICATION = 'acdc_config.wsgi.application'
ASGI_APPLICATION = 'acdc_config.asgi.application'

# ─────────────────────────────────────────────
# DATABASE — Remote VPS PostgreSQL  (SQLite offline fallback)
# Auto-detects VPS reachability; falls back to SQLite if unreachable.
# ─────────────────────────────────────────────
import socket as _socket
def _can_reach(host, port, timeout=3):
    try:
        s = _socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False

_pg_host = config('DATABASE_HOST', default='localhost')
_pg_port = int(config('DATABASE_PORT', default='5432'))
_USE_LOCAL = config('USE_LOCAL_DB', default=False, cast=bool) or not _can_reach(_pg_host, _pg_port)

if _USE_LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_local.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME'),
            'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
            'CONN_MAX_AGE': 30,   # reconnect every 30s max — prevents stale VPS connections
            'CONN_HEALTH_CHECKS': True,  # Django 4.1+ — validate connection before reuse
            'OPTIONS': {
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 5,
                'keepalives_count': 5,
                'application_name': 'shamel_local',
            },
        }
    }


# ─────────────────────────────────────────────
# CACHING — Local in-process memory (zero latency, no VPS round-trip)
# ─────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'shamel-main',
        'TIMEOUT': 300,
        'OPTIONS': {'MAX_ENTRIES': 2000},
    }
}

# Sessions stored locally on disk — no VPS hit for session lookups
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = None  # uses tempfile default

# ─────────────────────────────────────────────
# FACE RECOGNITION ENGINE
#   'dlib'        — legacy face_recognition (128-dim). Default: zero change
#                   to existing deployments and stored embeddings.
#   'insightface' — buffalo_s ONNX CPU (512-dim). Faster + more accurate on
#                   the weak VPS. Requires re-enrolling faces:
#                       python manage.py reenroll_faces
# Switch with env var FACE_ENGINE=insightface (no code change needed).
# ─────────────────────────────────────────────
FACE_ENGINE    = config('FACE_ENGINE', default='dlib')
FACE_THRESHOLD = config('FACE_THRESHOLD', default=0.35, cast=float)  # insightface cosine
FACE_TOLERANCE = config('FACE_TOLERANCE', default=0.5, cast=float)   # dlib euclidean


# ─────────────────────────────────────────────
# AUTHENTICATION BACKENDS (django-axes)
# ─────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_ENABLED = config('AXES_ENABLED', default=True, cast=bool)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25  # 15 minutes lockout


# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────────
# Suppress W042 — explicit primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LANGUAGE_CODE = 'ar'          # Arabic-first UI: localizes timesince, |date month/day names
TIME_ZONE = 'Africa/Khartoum'
USE_I18N = True
USE_L10N = True               # locale-aware number/date formatting (Arabic)
USE_TZ = False
DATE_FORMAT = 'd/m/Y'         # dd/mm/yyyy — not the US mm/dd/yyyy default
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'


# ─────────────────────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'attendance' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@shamel.edu.sd')


# ─────────────────────────────────────────────
# AUTH REDIRECTS
# ─────────────────────────────────────────────
LOGIN_URL = '/attendance/login/'
LOGIN_REDIRECT_URL = '/attendance/'


# ─────────────────────────────────────────────
# CHANNELS
# ─────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}


# ─────────────────────────────────────────────
# ENCRYPTION KEY (for sensitive data)
# ─────────────────────────────────────────────
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default='')


# ─────────────────────────────────────────────
# PRODUCTION SECURITY HARDENING
# ─────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
