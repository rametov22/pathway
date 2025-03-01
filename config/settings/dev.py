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

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None
SESSION_ENGINE = "django.contrib.sessions.backends.db"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Введите JWT-токен в формате: Bearer <token>",
        }
    },
    "USE_SESSION_AUTH": False,
}

STATIC_URL = "static/"
STATIC_DIR = BASE_DIR / "static_dev"
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = BASE_DIR / "static"
