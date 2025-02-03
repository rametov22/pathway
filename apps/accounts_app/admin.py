from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "id",
        "is_active",
    )
    search_fields = ("email",)
    list_filter = (
        "gender",
        "country",
        "is_active",
    )
    filter_horizontal = ("interests",)


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
    )
