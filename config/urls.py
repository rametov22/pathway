from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API документация",
        default_version="v1",
        description="Документация API проекта",
        terms_of_service="https://your-terms.com",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

schema_view.authentication_classes = []

schema_view.security_definitions = {
    "Bearer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "Введите JWT-токен в формате: Bearer <token>",
    }
}


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path(
            "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"
        ),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("api/v1/accounts/", include("apps.accounts_app.urls")),
        path("api/v1/universities/", include("apps.universities_app.urls")),
        path("api/v1/services/", include("apps.services_app.urls")),
        path("api/v1/news/", include("apps.news_app.urls")),
        path("api/v1/additionals/", include("apps.additionals_app.urls")),
        path("api/v1/experts/", include("apps.experts_app.urls")),
        path("api/v1/test/", include("apps.tests_app.urls")),
        path("mdeditor/", include("mdeditor.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + debug_toolbar_urls()
)
