from .base import *

ALLOWED_HOSTS = ["localhost", "172.30.82.188"]

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
