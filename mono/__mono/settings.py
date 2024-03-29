"""Django settings"""
import os
import sys
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from .__version__ import VERSION

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

APP_ENV = "TEST" if "pytest" in sys.modules else os.getenv("APP_ENV", "PRD")

APP_VERSION = VERSION

if APP_ENV in ["DEV", "TEST"]:
    GITHUB_SECRET = "GITHUB_SECRET"
else:  # pragma: no cover
    GITHUB_SECRET = os.getenv("GITHUB_SECRET")

# SECURITY WARNING: keep the secret key used in production secret!
if APP_ENV in ["DEV", "TEST"]:
    SECRET_KEY = "devkeyprojectmono"
else:  # pragma: no cover
    SECRET_KEY = os.getenv("APP_SECRET")

# For django-recaptcha
if APP_ENV in ["DEV", "TEST"]:
    SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
else:  # pragma: no cover
    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_PRIVATE_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = APP_ENV in ["DEV", "TEST"]
CSRF_COOKIE_SECURE = APP_ENV == "PRD"
SESSION_COOKIE_SECURE = APP_ENV == "PRD"
SECURE_SSL_REDIRECT = APP_ENV == "PRD"


if APP_ENV in ["DEV", "TEST"]:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(
        ","
    )  # pragma: no cover

if APP_ENV in ["DEV", "TEST"]:
    SITE = "http://127.0.0.1:8080"
else:
    SITE = "https://rodrigokimura.com"  # pragma: no cover

NOTIFICATION_CHECKER = (
    str(os.getenv("NOTIFICATION_CHECKER", "True")).lower() == "true"
)

# Application definition
INSTALLED_APPS = [
    "tinymce",
    "__mono.apps.MyAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "django.contrib.humanize",
    "maintenance_mode",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "social_django",
    "markdownx",
    "captcha",
    "background_task",
    "feedback",
    "healthcheck",
    "shared",
    "accounts",
    "homepage",
    "project_manager",
    "messenger",
    "finance",
    "blog",
    "checklists",
    "notes",
    "pixel",
    "watcher",
    "restricted_area",
    "shipper",
    "curriculum_builder",
    "coder",
    "mind_maps",
    "typer",
    "django.forms",
]

MIDDLEWARE = [
    "watcher.middlewares.StatisticsStartMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
    "watcher.middlewares.StatisticsFinishMiddleware",
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

ROOT_URLCONF = "__mono.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "_templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "__mono.context_processors.environment",
                "__mono.context_processors.language_extras",
                "__mono.context_processors.apps_menu",
                "accounts.context_processors.unread_notification_count",
                "pixel.context_processors.site",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "maintenance_mode.context_processors.maintenance_mode",
            ],
        },
    },
]

WSGI_APPLICATION = "__mono.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if APP_ENV in ["DEV", "TEST"]:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:  # pragma: no cover
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.getenv("DB_ADDR"),
            "PORT": "5432",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASS"),
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_ADDR', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}",
    }
}

AUTHENTICATION_BACKENDS = [
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.facebook.FacebookOAuth2",
    "__mono.auth_backends.EmailOrUsernameModelBackend",
]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

LOCALE_PATHS = [os.path.join(BASE_DIR, "_locale")]

LANGUAGE_EXTRAS = [
    ("en-us", _("American English"), "us", "en-US"),
    ("pt-br", _("Brasilian Portuguese"), "br", "pt-BR"),
]

LANGUAGES = tuple(
    (code, name) for code, name, flag, js_locale in LANGUAGE_EXTRAS
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(BASE_DIR, "_static")
MEDIA_ROOT = os.path.join(BASE_DIR, "_media")

LOGIN_URL = reverse_lazy("accounts:login")
LOGOUT_URL = reverse_lazy("home")
LOGIN_REDIRECT_URL = reverse_lazy("home")

if APP_ENV in ["DEV", "TEST"]:
    EMAIL_BACKEND = os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.console.EmailBackend",
    )
else:  # pragma: no cover
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 60

DEFAULT_FROM_EMAIL = "admin@monoproject.info"

ADMINS = [("Rodrigo Eiti Kimura", "rodrigoeitikimura@gmail.com")]
SERVER_EMAIL = "admin@monoproject.info"
EMAIL_SUBJECT_PREFIX = "[MONO PROJECT] "
EMAIL_USE_LOCALTIME = True

PASSWORD_RESET_TIMEOUT = 24 * 60 * 60

CHANGELOG_FILE = BASE_DIR.parent / "CHANGELOG.md"
PYTEST_REPORT_LOG = BASE_DIR / "reports" / "pytest" / "report.json"

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
STRIPE_TIMEZONE = os.getenv("STRIPE_TIMEZONE")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
}

FIREBASE_AUTH_FILE = BASE_DIR.parent / os.getenv(
    "FIREBASE_AUTH_FILE", "firebase_auth.json"
)

# SOCIAL LOGIN SECRETS
SOCIAL_AUTH_GITHUB_KEY = os.getenv("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("SOCIAL_AUTH_GITHUB_SECRET")

SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy("accounts:config")
SOCIAL_AUTH_LOGIN_REDIRECT_URL = reverse_lazy("accounts:config")
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# MAINTENANCE MODE
MAINTENANCE_MODE_IGNORE_SUPERUSER = True

if APP_ENV == "PRD":  # pragma: no cover
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "include_html": True,
            },
            "watcher": {
                "level": "ERROR",
                "class": "watcher.log_handlers.WatcherHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "mail_admins", "watcher"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "formatters": {
            "django.server": {
                "()": "__mono.log.CustomServerFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "django.db.backends": {
                "()": "__mono.log.CustomDatabaseFormatter",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
            },
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "django.db.backends": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "django.db.backends",
            },
            "mail_admins": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django.utils.log.AdminEmailHandler",
                "include_html": True,
            },
            "watcher": {
                "level": "ERROR",
                "class": "watcher.log_handlers.WatcherHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "mail_admins", "watcher"],
                "level": "INFO",
            },
            "django.server": {
                "handlers": ["django.server"],
                "propagate": False,
                "level": "INFO",
            },
            "django.db.backends": {
                "handlers": ["django.db.backends"],
                "propagate": False,
                "level": "DEBUG",
            },
        },
    }

WATCHER_REQUEST_RATE = int(os.getenv("WATCHER_REQUEST_RATE", "10"))


TINYMCE_DEFAULT_CONFIG = {
    "height": "320px",
    "width": "960px",
    "skin": "oxide-dark",
    "content_css": "dark",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
}

# TINYMCE_FILEBROWSER = False
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, "tinymce")


FILEBROWSER_DIRECTORY = os.path.join(MEDIA_ROOT, "uploads")
DIRECTORY = ""

# MARKDOWNX
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown_checklist.extension",
]

if APP_ENV == "TEST":
    import warnings

    warnings.simplefilter("ignore", Warning)
