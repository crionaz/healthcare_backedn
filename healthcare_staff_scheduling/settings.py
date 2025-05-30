from pathlib import Path
import os
from django.templatetags.static import static
from django.urls import reverse_lazy


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-1$!8oo4j5wc%fr*ylds!&-kq)uv5x&hd#o_8f^up(6dm=oe9ma'
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
CORS_ALLOW_ALL_ORIGINS = True



# Application definition

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    # 'staff_management.apps.StaffManagementConfig',
    'staff',
    'department',
    'role',
    'shift',
    'attendance',
    'api',
    'auth_api',
    
    # Third party apps
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',

    
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Crispy forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'healthcare_staff_scheduling.urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'healthcare_staff_scheduling.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "formula" / "static"]

STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login redirect URLs
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# Email settings for password reset (use console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Basic authentication using username and password'
        }
    },
    'DOC_EXPANSION': 'none',
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
}


UNFOLD = {
    "SITE_TITLE": "Healthcare Staff Scheduling",
    "SITE_DESCRIPTION": "A sample application for managing healthcare staff scheduling.",
    "SITE_FOOTER": "© 2025 Healthcare Staff Scheduling. All rights reserved.",
    "SITE_HEADER": "Healthcare Staff Scheduling",
    "SITE_SUBHEADER": "Manage your healthcare staff efficiently",
   
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    "SHOW_BACK_BUTTON": True, # show/hide "Back" button on changeform in header, default: False
    "ENVIRONMENT": "DEV", # environment name in header
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "base": {
            "50": "249, 250, 251",
            "100": "243, 244, 246",
            "200": "229, 231, 235",
            "300": "209, 213, 219",
            "400": "156, 163, 175",
            "500": "107, 114, 128",
            "600": "75, 85, 99",
            "700": "55, 65, 81",
            "800": "31, 41, 55",
            "900": "17, 24, 39",
            "950": "3, 7, 18",
        },
        "primary": {
            "50": "250, 245, 255",
            "100": "243, 232, 255",
            "200": "233, 213, 255",
            "300": "216, 180, 254",
            "400": "192, 132, 252",
            "500": "168, 85, 247",
            "600": "147, 51, 234",
            "700": "126, 34, 206",
            "800": "107, 33, 168",
            "900": "88, 28, 135",
            "950": "59, 7, 100",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },

    # "SIDEBAR": {
    #     "show_search": False,  # Search in applications and models names
    #     "show_all_applications": True,  # Dropdown with all applications and models
    #     "navigation": [
    #         {
    #             "title": "Staff Management",
    #             "separator": True,  # Top border
    #             "collapsible": True,  # Collapsible group of links
    #             "items": [
    #                 {
    #                     "title": "Dashboard",
    #                     "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
    #                     "link": reverse_lazy("admin:index"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 {
    #                     "title": "Staff Members",
    #                     "icon": "people",
    #                     "link": reverse_lazy("admin:staff_staffmember_changelist"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 # {
    #                 #     "title": "Base User",
    #                 #     "icon": "users",
    #                 #     "link": reverse_lazy("admin:auth.user_changelist"),
    #                 #     # "permission": lambda request: request.user.is_superuser,
    #                 # },
    #             ],
    #         },
    #         {
    #             "title": "Departments",
    #             "separator": True,  # Top border
    #             "collapsible": True,  # Collapsible group of links
    #             "items": [
    #                 {
    #                     "title": "Department List",
    #                     "icon": "list",
    #                     "link": reverse_lazy("admin:department_department_changelist"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 {
    #                     "title": "Add Department",
    #                     "icon": "add",
    #                     "link": reverse_lazy("admin:department_department_add"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #             ],
    #         },
    #         {
    #             "title": "Roles Management",
    #             "separator": True,  # Top border
    #             "collapsible": True,  # Collapsible group of links
    #             "items": [
    #                 {
    #                     "title": "Role List",
    #                     "icon": "list",
    #                     "link": reverse_lazy("admin:role_role_changelist"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 {
    #                     "title": "Add Role",
    #                     "icon": "add",
    #                     "link": reverse_lazy("admin:role_role_add"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #             ],
    #         },
    #         {
    #             "title": "Shift Management",
    #             "separator": True,  # Top border
    #             "collapsible": True,  # Collapsible group of links
    #             "items": [
    #                 {
    #                     "title": "Shift List",
    #                     "icon": "list",
    #                     "link": reverse_lazy("admin:shift_shift_changelist"),
    #                 },
    #                 {
    #                     "title": "Add Shift",
    #                     "icon": "add",
    #                     "link": reverse_lazy("admin:shift_shift_add"),
    #                     # "permission": lambda request: request.user.is_superuser,
    #                 },
    #                 {
    #                     "title": "Shift Swap Requests",
    #                     "icon": "swap_horiz",
    #                     "link": reverse_lazy("admin:shift_swaprequest_changelist"),
    #                 },
    #                 {
    #                     "title": "Shift Assignments",
    #                     "icon": "assignment",
    #                     "link": reverse_lazy("admin:shift_shiftassignment_changelist"),
    #                 },
    #             ],
    #         },
    #     ]
    # },
    # "TABS": [
    #     {
    #         "models": [
    #             "app_label.model_name_in_lowercase",
    #         ],
    #         "items": [
    #             {
    #                 "title": _("Your custom title"),
    #                 "link": reverse_lazy("admin:app_label_model_name_changelist"),
    #                 "permission": "sample_app.permission_callback",
    #             },
    #         ],
    #     },
    # ],
}
