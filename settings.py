# Django settings for rbx-django project.
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

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
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ACTSTREAM_SETTINGS = {
    'MODELS': ('auth.user', 'rbx.project', 'rbx.Box', 'rbx.Run'),
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
}

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'urls'

X_FRAME_OPTIONS = 'DENY'

AUTH_PROFILE_MODULE = 'rbx.UserProfile'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'haystack',
    'django_gravatar',
    'crispy_forms',
    'markdown_deux',
    'rbx',
    'actstream',
    'south',
)

COMMON_ERROR_MSG = 'Oops, something wrong happened, please try again...'

GRAVATAR_DEFAULT_URL = 'mm'

VIEW_RIGHT = 0
EDIT_RIGHT = 1
ADMIN_RIGHT = 2

HAYSTACK_SITECONF = 'rbx.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = '/tmp/whoosh/rbx_index'

CLOUD_AUTH = 'jexhson:stratusBldy1'
CLOUD_ENDPOINT = 'https://%s@cloud.lal.stratuslab.eu:2634/pswd/xmlrpc' % CLOUD_AUTH
PUBLIC_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPD3/cMQtrfIN9z180vj7wh2chyrgH1qjBn6VrxZ/7s1a7lxRbb8e+ghpisg+wn63qQ8EbQ+6lAqO2sNvfBzTwRik51zvwlAzIGStSJAXex9IM6txpaQQl2MmAn6zRC7mvXgrPfE8Ey3TZkCHUBFjG2bjv9Qaa6udEmZd2bwD0N/X+h3QyeMfdrINRFlHKoCoEn5w0k1VtLzllSL/ovJLfGpyhSmx7W7JHtbOIW0GGLFwpHubb38quboHqtzWyGTFxVCxZSoC+XI/sli1XSsqPIuuFLqgVCtE112ESkNKb39i8AZL7+gh102B34UnSl05PJHJNb0Yv3Xq77FDRu8Ct'

RESULT_URL = 'results/'
STORAGE = '/home/jexhson/code/rbx-django/rbx/static/'
