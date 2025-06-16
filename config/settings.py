"""
 Django settings for config project.
 (مُبسّط – منسّق – جاهز للنسخ)
"""

# ---------------------------------------------------------------------------
# المسارات
# ---------------------------------------------------------------------------
from pathlib import Path
import os

# (اختياري) تحميل متغيّرات .env إن كنت تستخدم python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    # لم تُثبَّت python-dotenv، تجاهل السطرين السابقين
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# مفاتيح الأمان
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-kg6i*-!s*e_vgu05l5ofpwi0g$!30wf71=(@o=ph(_^c5e_9d0",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# ---------------------------------------------------------------------------
# التطبيقات المثبَّتة
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # تطبيقاتك الداخلية
    "core",
]


# ---------------------------------------------------------------------------
# الوسطاء (Middleware)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------------------------
# توجيه العناوين
# ---------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------------------------
# القوالب (Templates)
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",  # لـ Tailwind
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------------------------
# بوابة WSGI
# ---------------------------------------------------------------------------
WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# قاعدة البيانات
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     os.environ.get("POSTGRES_DB",       "majedlearn_db"),
        "USER":     os.environ.get("POSTGRES_USER",     "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST":     os.environ.get("POSTGRES_HOST",     "127.0.0.1"),
        "PORT":     os.environ.get("POSTGRES_PORT",     "5432"),
    }
}


# ---------------------------------------------------------------------------
# التحقق من كلمات المرور
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# الإعدادات الإقليمية
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "ar"
TIME_ZONE     = "Asia/Riyadh"
USE_I18N      = True
USE_TZ        = True


# ---------------------------------------------------------------------------
# الملفات الثابتة والميديا
# ---------------------------------------------------------------------------
STATIC_URL       = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]     # أثناء التطوير
STATIC_ROOT      = BASE_DIR / "staticfiles"  # عند التحزيم

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# البريد الإلكتروني (طور الإنتاج)
# ---------------------------------------------------------------------------
EMAIL_BACKEND      = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST         = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT         = int(os.environ.get("EMAIL_PORT", 25))
EMAIL_HOST_USER    = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD= os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS      = os.environ.get("EMAIL_USE_TLS", "False") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")

# (أثناء التطوير يمكنك تفعيل backend الكونسول)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ---------------------------------------------------------------------------
# الحقل الافتراضي
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
