from .base import *

ALLOWED_HOSTS = ["www.pthwy.co", "pthwy.co", "localhost"]

CSRF_TRUSTED_ORIGINS = ["https://pthwy.co", "https://www.pthwy.co"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
