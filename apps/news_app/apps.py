from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.news_app"

    def ready(self):
        import apps.news_app.signals
