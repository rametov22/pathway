from .base import *

ALLOWED_HOSTS = ["www.pthwy.co", "pthwy.co"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "pathway_db",
        "USER": "pathway_user",
        "PASSWORD": "Rr25808773",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
