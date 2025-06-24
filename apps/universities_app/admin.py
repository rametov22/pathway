from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import Directions, Universities, Country


@admin.register(Universities)
class UniversitiesAdmin(TabbedTranslationAdmin):
    list_display = (
        "university_name",
        "id",
    )
    filter_horizontal = ("university_directions",)


@admin.register(Country)
class CountryAdmin(TabbedTranslationAdmin):
    list_display = (
        "name",
        "manual_order",
        "id",
    )
    list_editable = ("manual_order",)


@admin.register(Directions)
class DirectionsAdmin(TabbedTranslationAdmin):
    list_display = (
        "direction",
        "id",
    )
