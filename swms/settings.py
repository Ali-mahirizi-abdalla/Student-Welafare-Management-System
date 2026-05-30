import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# BASE DIRECTORY
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY
# ============================================
SECRET_KEY = os.getenv('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ✅ ALLOWED HOSTS — controlled via ALLOWED_HOSTS env var on Render
_allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()] or [
    'campus-care.co.ke',
    'www.campus-care.co.ke',
    'swms-web.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

# CSRF protection
CSRF_TRUSTED_ORIGINS = [
    'https://campus-care.co.ke',
    'https://www.campus-care.co.ke',
    'http://campus-care.co.ke',
    'http://www.campus-care.co.ke',
    'https://swms-web.onrender.com',
    'https://*.onrender.com',
    'https://38.247.148.232',
    'http://38.247.148.232',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'https://*.ngrok-free.dev',
    'http://127.0.0.1',
    'http://localhost',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Allow overriding via environment variable
_csrf_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _csrf_env:
    CSRF_TRUSTED_ORIGINS.extend([h.strip() for h in _csrf_env.split(',') if h.strip()])

# Dynamically add all ALLOWED_HOSTS to CSRF_TRUSTED_ORIGINS to prevent 403s
for host in ALLOWED_HOSTS:
    clean_host = host.lstrip('.')
    if clean_host and clean_host not in ['*', 'localhost', '127.0.0.1']:
        CSRF_TRUSTED_ORIGINS.extend([f'https://{clean_host}', f'http://{clean_host}'])


# CSRF Cookie Settings
CSRF_USE_SESSIONS = False  # Switch back to cookie-based for robustness
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_DOMAIN = None

if DEBUG:
    CSRF_COOKIE_SECURE = False
    CSRF_TRUSTED_ORIGINS += [
        'http://38.247.148.232',
        'https://38.247.148.232',
        'http://38.247.148.232:8000',
        'https://38.247.148.232:8000',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]
else:
    CSRF_COOKIE_SECURE = True

# Production security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Proxy & CSRF Fix for Cloudflare/Nginx/Ngrok
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ============================================
# INSTALLED APPS
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'hms',  # Your app


    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Google provider only loaded if credentials are configured (requires 'cryptography' package)

    
    # Whitenoise
    'whitenoise.runserver_nostatic',

    # Backup
    'dbbackup',
    
    # REST Framework
    'rest_framework',

    # Scalability & Storage
]

# Only load Google OAuth provider if credentials are set (it requires 'cryptography' package)
if os.getenv('GOOGLE_CLIENT_ID'):
    INSTALLED_APPS += ['allauth.socialaccount.providers.google']

SITE_ID = 1

# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'hms.middleware.AuditMiddleware',
    'hms.middleware.PresenceMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ============================================
# URL CONFIG
# ============================================
ROOT_URLCONF = 'swms.urls'

# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': False,  # Set to False when using explicit loaders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hms.context_processors.unread_messages',
                'hms.context_processors.staff_role_info',
                'hms.context_processors.unread_notifications',
                'hms.context_processors.telegram_info',
            ],
            # Explicitly disable template caching in DEBUG mode
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ] if DEBUG else [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

WSGI_APPLICATION = 'swms.wsgi.application'

# ============================================
# DATABASE
# ============================================
# Database Configuration
# Priority: DATABASE_URL > Environment Components > SQLite (if USE_SQLITE=True)
if os.getenv('USE_SQLITE', 'False') == 'True' and not os.getenv('DATABASE_URL'):
    render_disk = os.getenv('RENDER_DISK_DIR')
    if render_disk:
        sqlite_path = Path(render_disk) / 'db.sqlite3'
    else:
        sqlite_path = BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_path,
        }
    }
else:
    # Production Database (PostgreSQL/MySQL)
    if os.getenv('DATABASE_URL'):
        DATABASES = {
            'default': dj_database_url.config(
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        # Fallback to manual components (MySQL) ONLY if explicit MySQL environment variables exist
        if os.getenv('DB_NAME') and os.getenv('DB_USER') and 'mysql' in os.getenv('DB_ENGINE', '').lower():
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': os.getenv('DB_NAME', 'swms_db'),
                    'USER': os.getenv('DB_USER', 'root'),
                    'PASSWORD': os.getenv('DB_PASSWORD', ''),
                    'HOST': os.getenv('DB_HOST', 'localhost'),
                    'PORT': os.getenv('DB_PORT', '3306'),
                    'OPTIONS': {
                        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                        'charset': 'utf8mb4',
                    },
                }
            }
        else:
            # Safe ultimate fallback to SQLite so the build command doesn't crash
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }

# Persistent Database Connections (Performance)
# Keep connections alive for 600 seconds (10 mins) to reduce overhead
DATABASES['default']['CONN_MAX_AGE'] = 600


# ============================================
# PASSWORD VALIDATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ============================================
# INTERNATIONALIZATION
# ============================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC FILES
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'hms/static')]


# ============================================
# MEDIA FILES
# ============================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ============================================
# DEFAULT PRIMARY KEY FIELD
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# AUTHENTICATION
# ============================================
LOGIN_URL = 'hms:login'
LOGIN_REDIRECT_URL = 'hms:student_dashboard'
LOGOUT_REDIRECT_URL = 'hms:login'

AUTHENTICATION_BACKENDS = [
    'hms.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'optional'
# settings.ACCOUNT_AUTHENTICATION_METHOD is deprecated
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
# settings.ACCOUNT_EMAIL_REQUIRED and ACCOUNT_USERNAME_REQUIRED are deprecated
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}

# ============================================
# EMAIL CONFIGURATION
# ============================================
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'alimahrez744@gmail.com')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f'Student Welfare Management System (SWMS) <onboarding@resend.dev>')

if DEBUG:
    # Use real email for testing if credentials exist, else console
    if os.environ.get('EMAIL_HOST_PASSWORD'):
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Use Resend by default, but allow overrides
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.resend.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'resend')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 're_gnrHihB4_EQqvTBYmmtNsmSdmfDmWEHKk')

# ============================================
# AFRICA'S TALKING (SMS)
# ============================================
AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY', '')
AFRICASTALKING_SENDER_ID = os.environ.get('AFRICASTALKING_SENDER_ID', '')

# ============================================
# CACHING (Redis)
# ============================================
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }


# ============================================
# MPESA CONFIGURATION 
# ============================================
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379') # Sandbox Paybill
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '') # Sandbox Passkey
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'https://campus-care.co.ke/payment/callback/')


# ============================================
# STORAGES (Django 4.2+)
# ============================================
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "dbbackup": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": os.path.join(BASE_DIR, "backups"),
        },
    },
}

# ============================================
# CLOUD STORAGE CONFIGURATION
# ============================================
USE_S3 = os.getenv('USE_S3') == 'True'
USE_CLOUDINARY = os.getenv('USE_CLOUDINARY') == 'True'

if USE_S3:
    # AWS S3 Settings
    if 'storages' not in INSTALLED_APPS:
        INSTALLED_APPS += ['storages']
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }
    
elif USE_CLOUDINARY:
    # Cloudinary Settings
    if 'cloudinary' not in INSTALLED_APPS:
        INSTALLED_APPS += ['cloudinary']
    if 'cloudinary_storage' not in INSTALLED_APPS:
        INSTALLED_APPS += ['cloudinary_storage']
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
        'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    }
    
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }


DBBACKUP_STORAGE_ALIAS = 'dbbackup'


# Add MySQL to PATH for dbbackup (Windows only)
if os.name == 'nt':
    mysql_path = r'C:\Program Files\MySQL\MySQL Server 8.0\bin'
    if mysql_path not in os.environ['PATH']:
        os.environ['PATH'] += ';' + mysql_path

# Select DBBackup connector dynamically depending on the active database engine
db_engine = DATABASES['default']['ENGINE']
if 'postgresql' in db_engine or 'postgres' in db_engine:
    DBBACKUP_CONNECTORS = {
        'default': {
            'CONNECTOR': 'dbbackup.db.postgresql.PgDumpConnector',
        }
    }
elif 'mysql' in db_engine:
    DBBACKUP_CONNECTORS = {
        'default': {
            'CONNECTOR': 'dbbackup.db.mysql.MysqlDumpConnector',
        }
    }
else:
    DBBACKUP_CONNECTORS = {
        'default': {
            'CONNECTOR': 'dbbackup.db.sqlite.SqliteConnector',
        }
    }

# ============================================
# TELEGRAM BROADCAST CONFIGURATION
# ============================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')




