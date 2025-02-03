from .base import *

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "pathway_db",
        "USER": "postgres",
        "PASSWORD": "0022",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
