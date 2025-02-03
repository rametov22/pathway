from django.contrib import admin
from django.db import models

from mdeditor.widgets import MDEditorWidget

from .models import *


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": MDEditorWidget}}


@admin.register(ConsultationRequest)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "created_at")
    readonly_fields = ("created_at",)
    list_filter = ("created_at",)
