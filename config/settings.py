import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-v12games-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# التطبيقات المثبتة
INSTALLED_APPS = [
    'jazzmin',                      # لوحة الادمن الجميلة
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',                      # نظام تسجيل الدخول
    'allauth.account',
    'allauth.socialaccount',
    'django_filters',               # فلترة الألعاب
    'games',                        # تطبيق الألعاب
    'accounts',                     # تطبيق المستخدمين
    'reviews',                      # تطبيق التقييمات
    'blog',                         # تطبيق المدونة
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# قاعدة البيانات
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# المستخدم المخصص
AUTH_USER_MODEL = 'accounts.User'
SITE_ID = 1

# إعدادات تسجيل الدخول
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# البريد الإلكتروني (للتطوير فقط)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# إعدادات allauth
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']

# الملفات الثابتة
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ملفات الميديا (الصور)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# إعدادات لوحة الادمن
JAZZMIN_SETTINGS = {
    'site_title': 'V12Games Admin',
    'site_header': 'V12Games',
    'site_brand': '🎮 V12Games',
    'welcome_sign': 'مرحباً بك في لوحة تحكم V12Games',
    'theme': 'darkly',
    'icons': {
        'games.game': 'fas fa-gamepad',
        'games.genre': 'fas fa-tags',
        'games.collection': 'fas fa-layer-group',
        'reviews.review': 'fas fa-star',
        'blog.post': 'fas fa-newspaper',
        'accounts.user': 'fas fa-user',
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

RAWG_API_KEY = os.getenv('RAWG_API_KEY', '')
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
DISCORD_WEBHOOK_URL = os.getenv('https://discord.com/api/webhooks/1482514602754441447/Ctb0feZr0zkUZkdNTg8qR7QGOHW8ZFzmz2ik2YZbDeM8fzvy7claznHEAOn1BSFQYYm1', '')