#encoding:utf-8
import os
from google.appengine.api import rdbms

#from google.appengine.api import logservice
#logservice.AUTOFLUSH_ENABLED=False

from google.appengine.api import logservice
logservice.AUTOFLUSH_EVERY_SECONDS=None
logservice.AUTOFLUSH_EVERY_BYTES=None
logservice.AUTOFLUSH_EVERY_LINES=20
# Django settings for oClockDjango project.
DEBUG=False
TEMPLATE_DEBUG=DEBUG
APPEND_SLASH=True
ADMINS=(
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS=ADMINS
if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    # Running on production App Engine, so use a Google Cloud SQL database.
    DATABASES={
        'default':{
            'ENGINE':'django.db.backends.mysql',
            'HOST':'/cloudsql/festive-ally-585:oclock',
            'NAME':'oclock',
            'USER':'root',
        }
    }
elif os.getenv('SETTINGS_MODE') == 'prod':
    # Running in development, but want to access the Google Cloud SQL instance
    # in production.
    DATABASES = {
        'default': {
            'ENGINE': 'google.appengine.ext.django.backends.rdbms',
            'INSTANCE': 'festive-ally-585:oclock',
            'NAME': 'oclock',
            'USER': 'root',
        }
    }
else:
    # Running in development, so use a local MySQL database.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'oclock',
            'USER': 'root',
            'PASSWORD': 'root',
        }
    }
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

STATIC_ROOT = '/oclock'

STATIC_URL = '/static/'

#os.environ['DJANGO_SETTINGS_MODULE'] = 'Django_AppEngine.settings'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'et(yykx4w51zp&g9)90%@h_14efe!b$gqz^a0*cp!xaan*@w&m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
      'django.template.loaders.filesystem.Loader',
      'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'oauth2_provider.middleware.OAuth2TokenMiddleware',
    #'django_user_agents.middleware.UserAgentMiddleware',
)

FILE_UPLOAD_HANDLERS=(
 'django.core.files.uploadhandler.MemoryFileUploadHandler',
 'django.core.files.uploadhandler.TemporaryFileUploadHandler',)
#FILE_UPLOAD_HANDLERS=('django.core.files.uploadhandler.MemoryFileUploadHandler',)
FILE_UPLOAD_MAX_MEMORY_SIZE=10621440

ROOT_URLCONF='Django_AppEngine.urls'

ROOT_PATH=os.path.dirname(__file__)

#from unipath import Path
#PROJECT_DIR = Path(__file__).ancestor(3)

TEMPLATE_DIRS=(
    os.path.join(ROOT_PATH, "templates"),
    #PROJECT_DIR.child("allauth").child("templates"),
)

INSTALLED_APPS=(
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'oclock',
    #'tastypie',
    'rest_framework',
    'provider',
    'provider.oauth2',
    #'django_facebook',
    #'allauth',
    #'allauth.account',
    #'allauth.socialaccount',
    # ... include the providers you want to enable:
    #'allauth.socialaccount.providers.facebook',
    #'django.contrib.sites'
    'sslify',
    #'django_user_agents',
)

import json
GOOGLEPLUS_CLIENT_ID = '420949186966-7sm0ck70ioh8hkj3tlkte26k3b0ab7o9.apps.googleusercontent.com'
GOOGLEPLUS_CLIENT_SECRET = 'yEGuHSRjOlB065DRzGeRzdQx'

SCOPES = [
    'https://www.googleapis.com/auth/plus.login',
    'https://www.googleapis.com/auth/userinfo.email'
]

VISIBLE_ACTIONS = [
    'http://schemas.google.com/AddActivity',
    'http://schemas.google.com/ReviewActivity'
]

TOKEN_INFO_ENDPOINT = ('https://www.googleapis.com/oauth2/v1/tokeninfo' +
    '?access_token=%s')
TOKEN_REVOKE_ENDPOINT = 'https://accounts.google.com/o/oauth2/revoke?token=%s'

"""Base type which ensures that derived types always have an HTTP session."""
CURRENT_USER_SESSION_KEY = 'me'

# TODO: Replace the following lines with client IDs obtained from the APIs
# Console or Cloud Console.
WEB_CLIENT_ID = '420949186966-7sm0ck70ioh8hkj3tlkte26k3b0ab7o9.apps.googleusercontent.com'
ANDROID_CLIENT_ID = '420949186966-31vb315pfvd6mhm25q2g2975k7n2d8fn.apps.googleusercontent.com'
IOS_CLIENT_ID = '420949186966-s95113jpkipbhqb742qi0qao1lo5p1fb.apps.googleusercontent.com'
ANDROID_AUDIENCE = WEB_CLIENT_ID

MANDRILL_SMTP_USER = 'digitaldreami@gmail.com'
MANDRILL_SMTP_PASS = 'B5qyJYPbBP7aGKtegPHJXA'

#OAUTH2_PROVIDER = {
    # this is the list of available scopes
    #'SCOPES': ['read', 'write', 'groups']
#}

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #'DEFAULT_PERMISSION_CLASSES': [
    #    'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #],
    'DEFAULT_PERMISSION_CLASSES': (
        #'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
       #'rest_framework.authentication.TokenAuthentication',
       #'rest_framework.authentication.BasicAuthentication',
       #'rest_framework.authentication.SessionAuthentication',
       #'rest_framework.authentication.OAuth2Authentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.XMLRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    )
}

FACEBOOK_APP_ID=''
FACEBOOK_APP_SECRET=''

TEMPLATE_CONTEXT_PROCESSORS = (
    # Required by allauth template tags
    "django.core.context_processors.request",
    # allauth specific context processors
    #"allauth.account.context_processors.account",
    #"allauth.socialaccount.context_processors.socialaccount",
    
    'django.contrib.auth.context_processors.auth'
)

"""AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)"""

"""AUTH_PROFILE_MODULE = 'django_facebook.FacebookProfile'"""

"""SOCIALACCOUNT_PROVIDERS = \
    {'facebook':
       {'SCOPE': ['email', 'publish_stream'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'METHOD': 'oauth2',
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False}}"""

#FACEBOOK_APP_ID='233211403553992'
#FACEBOOK_APP_SECRET='0fc70b1a3d05df5ea58601f644e2e3cc'
FACEBOOK_APP_ID='407223625967266'
FACEBOOK_APP_SECRET='29ca9bb0f0740caab5a395a94112af8f'

SESSION_COOKIE_DOMAIN='oclck.com'
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_PATH='/'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_NAME='sid'
SESSION_COOKIE_AGE=300

ALLOWED_HOSTS = ['*']

SESSION_SAVE_EVERY_REQUEST=True

SECRET_KEY = '9a7!^gp8ojyk-^^d@*whuw!0rml+r+uaie4'

CSRF_COOKIE_SECURE=True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
SSLIFY_DISABLE=True
PHOTOLOGUE_MAXBLOCK=2048*2**10