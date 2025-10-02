from django.contrib import admin
from django.db import models
from modeltranslation.admin import TabbedTranslationAdmin, TranslationAdmin
from mdeditor.widgets import MDEditorWidget
from rangefilter.filters import DateRangeFilterBuilder

from .models import *


@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    formfield_overrides = {models.TextField: {"widget": MDEditorWidget}}
    filter_horizontal = ("experts",)


@admin.register(ServiceApplication)
class ServiceApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "status", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("user__email",)
    list_filter = (
        "service",
        "status",
        "created_at",
        ("created_at", DateRangeFilterBuilder()),
    )


@admin.register(ConsultationRequest)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "id",
        "status",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "answered_at",
    )
    list_filter = (
        "status",
        "created_at",
    )


@admin.register(DayOfWeeks)
class DayOfWeeksAdmin(TabbedTranslationAdmin):
    pass


@admin.register(ConsultationServices)
class ConsultationServicesAdmin(TabbedTranslationAdmin):
    pass


@admin.register(EducationLevels)
class EducationLevelsAdmin(TabbedTranslationAdmin):
    pass
