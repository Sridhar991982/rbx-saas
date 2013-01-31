# Django settings for rbx-django project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rbx.db',
    },
    'prod': {
        'ENGINE': 'django.db.backends.dummy',
        'NAME': 'rbx_django',
        'USER': 'rbx',
        'PASSWORD': '',
        'HOST': 'mysql2.alwaysdata.com',
    }
}

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False
USE_L10N = True

STATIC_URL = '/static/'

SECRET_KEY = 'rtu=46ty46r7yq7-o!i*p9l&jj)s%qd^@vs_*g&_7z1-n22$+g'

TEMPLATE_LOADERS = (
    #'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ACTSTREAM_SETTINGS = {
    'MODELS': ('rbx.UserProfile', 'rbx.Project', 'rbx.Executor'),
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
}

ROOT_URLCONF = 'urls'

AUTH_PROFILE_MODULE = 'rbx.UserProfile'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django_gravatar',
    'crispy_forms',
    'markdown_deux',
    'rbx',
    'actstream',
    'doc',
)

VIEW_RIGHT = 0
EDIT_RIGHT = 1
ADMIN_RIGHT = 2
