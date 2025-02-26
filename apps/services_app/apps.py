from django.apps import AppConfig


class ServicesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.services_app"

    def ready(self):
        import apps.services_app.signals
