from django.contrib import admin

from .models import Expert


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    pass
