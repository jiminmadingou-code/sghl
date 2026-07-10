from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Railway injecte automatiquement RAILWAY_PUBLIC_DOMAIN
_railway_host = config('RAILWAY_PUBLIC_DOMAIN', default='')
if _railway_host and _railway_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_host)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'channels',
    # Cache
    'redis',
    # SGHL apps
    'audit',
    'patients',
    'hospitalisations',
    'laboratoire',
    'pharmacie',
    'facturation',
    'personnel',
    'soins',
    'dashboard',
    'chat',
    'gardes',
    'rendez_vous',
    'prescriptions',
    'consentement',
    'email_service',
    'backup',
    'urgences',
    'imagerie',
    'bloc_operatoire',
    'maternite',
    'teleconsultation',
    'archivage',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.RateLimitMiddleware',
    'core.middleware.InputSanitizationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.RBACMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise pour servir les fichiers statiques en production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS — autorise tout (mobile Flutter, web, Railway)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization',
    'content-type', 'dnt', 'origin', 'user-agent',
    'x-csrftoken', 'x-requested-with',
]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── Cache : Redis si disponible, sinon LocMemCache ───────────────────────────
REDIS_URL = config('REDIS_URL', default='')
_redis_available = False
if REDIS_URL:
    try:
        import redis as _redis_lib
        _r = _redis_lib.from_url(REDIS_URL, socket_connect_timeout=1)
        _r.ping()
        _redis_available = True
    except Exception:
        pass

if _redis_available:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            }
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [REDIS_URL]},
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'sghl-local-cache',
        }
    }
    CHANNEL_LAYERS = {
        'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Email (SMTP)
EMAIL_BACKEND    = config('EMAIL_BACKEND',    default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST       = config('EMAIL_HOST',       default='smtp.gmail.com')
EMAIL_PORT       = config('EMAIL_PORT',       default=587, cast=int)
EMAIL_HOST_USER  = config('EMAIL_HOST_USER',  default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS    = config('EMAIL_USE_TLS',    default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='DIGNE HOSPITAL <noreply@sghl.cg>')

# ── Logging JSON structuré (compatible ELK / Elasticsearch) ──────────────────
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'core.log_formatter.SGHLJsonFormatter',
        },
        'console': {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        # Fichier JSON — ingérable par Filebeat → Elasticsearch → Kibana
        'json_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'sghl.json.log'),
            'maxBytes': 50 * 1024 * 1024,  # 50 MB
            'backupCount': 10,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        # Fichier dédié sécurité / antivirus
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'security.json.log'),
            'maxBytes': 20 * 1024 * 1024,
            'backupCount': 30,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
        # Fichier audit trail
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'audit.json.log'),
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 90,
            'formatter': 'json',
            'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['console', 'json_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django':         {'handlers': ['console', 'json_file'], 'level': 'WARNING',  'propagate': False},
        'sghl.antivirus': {'handlers': ['console', 'security_file'], 'level': 'DEBUG', 'propagate': False},
        'sghl.audit':     {'handlers': ['console', 'audit_file'],    'level': 'INFO',  'propagate': False},
        'sghl.security':  {'handlers': ['console', 'security_file'], 'level': 'INFO',  'propagate': False},
        'core.middleware': {'handlers': ['console', 'security_file'],'level': 'WARNING','propagate': False},
    },
}

# Security headers (production)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    # Railway : filesystem éphémère — logs console uniquement (pas de fichiers)
    for _h in ['json_file', 'security_file', 'audit_file']:
        LOGGING['handlers'][_h] = {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        }
