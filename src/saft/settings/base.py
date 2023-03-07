import os
from pathlib import Path

from decouple import config
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from saft.utils.graphql import GraphqlService, AREA

SECRET_KEY = config('SECRET_KEY')

BASE_DIR = Path(__file__).resolve().parent.parent.parent

VENV_PATH = BASE_DIR.parent

STATICFILES_DIRS = [BASE_DIR / 'static']

STATIC_ROOT = VENV_PATH / 'static_root'
MEDIA_ROOT = VENV_PATH / 'media'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'dal_admin_filters',
    'django_filters',
    'bootstrapform',
    'reportlab',

    'preventconcurrentlogins',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'saft.apps.inventory.apps.InventoryConfig',
    'saft.apps.people.apps.PeopleConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'preventconcurrentlogins.middleware.PreventConcurrentLoginsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'saft.urls'

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
ROOT_URLCONF = 'saft.urls'
LOGIN_URL = ''

WSGI_APPLICATION = 'saft.wsgi.application'

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
AUTH_USER_MODEL = 'people.User'

LANGUAGE_CODE = 'es-en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True  # para el cambio de idioma en fechas

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGES = (
    ('es', _('Spanish')),
    ('en', _('English')),
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = reverse_lazy('inventory:list_fixed_asset_user_view')

GRAPHQL_SERVICE = GraphqlService()
AREA = AREA
