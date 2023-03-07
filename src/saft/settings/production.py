from .base import *
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': config('DATABASE_NAME'),
    #     'USER': config("DATABASE_USER"),
    #     'PASSWORD': config('DATABASE_PASSWORD'),
    #     'HOST': config('DATABASE_HOST'),
    #     'PORT': config('DATABASE_PORT')
    # }
}