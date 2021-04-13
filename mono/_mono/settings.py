import os
from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_ENV = os.getenv('APP_ENV')

GITHUB_SECRET = os.getenv('GITHUB_SECRET')

# SECURITY WARNING: keep the secret key used in production secret!
if APP_ENV == 'DEV':
    SECRET_KEY = 'devkeyprojectmono'
else:
    SECRET_KEY = os.getenv('APP_SECRET')

# For django-recaptcha
if APP_ENV == 'DEV':
    SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
else:
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = APP_ENV == 'DEV'
CSRF_COOKIE_SECURE = APP_ENV == 'PRD'
SESSION_COOKIE_SECURE = APP_ENV == 'PRD'

if APP_ENV == 'DEV':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]

if APP_ENV == 'DEV':
    SITE = "http://dev.monoproject.info"
else:
    SITE = "https://www.monoproject.info"

# Application definition
INSTALLED_APPS = [
    '_mono.apps.MyAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytical',
    'django.contrib.admindocs',
    'rest_framework',
    'rest_framework.authtoken',
    # 'debug_toolbar',
    'captcha',
    'healthcheck',
    'shared',
    'accounts',
    'homepage',
    'project_manager',
    'messenger',
    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# INTERNAL_IPS = ['127.0.0.1']

# SHOW_TOOLBAR_CALLBACK = '.'
# SHOW_COLLAPSED = True

ROOT_URLCONF = '_mono.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                '_mono.context_processors.environment',
                '_mono.context_processors.language_extras',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = '_mono.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if APP_ENV == 'DEV':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASS'),
            'HOST': os.getenv('DB_ADDR'),
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

LANGUAGE_EXTRAS = [
    ('en-us', _('American English'), 'us', 'en-US'),
    ('pt-br', _('Brasilian Portuguese'), 'br', 'pt-BR'),
]

LANGUAGES = tuple((code, name) for code, name, flag, js_locale in LANGUAGE_EXTRAS)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = reverse_lazy('finance:index')
LOGIN_URL = reverse_lazy('finance:login')

if APP_ENV == 'DEV':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_TIMEOUT = 30

DEFAULT_FROM_EMAIL = 'no-reply@voitkemp.com'

ADMINS = [('Rodrigo Eiti Kimura', 'rodrigoeitikimura@gmail.com')]
SERVER_EMAIL = 'no-reply@voitkemp.com'
EMAIL_SUBJECT_PREFIX = '[MONO PROJECT] '
EMAIL_USE_LOCALTIME = True

PASSWORD_RESET_TIMEOUT = 24 * 60 * 60

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET')
STRIPE_TIMEZONE = os.getenv('STRIPE_TIMEZONE')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# ANALYTICAL APP CONFIG
CLICKY_SITE_ID = '101311237'
