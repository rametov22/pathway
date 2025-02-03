from django.contrib import admin
from .models import Directions, Universities, Country


@admin.register(Universities)
class UniversitiesAdmin(admin.ModelAdmin):
    list_display = (
        "university_name",
        "id",
    )
    filter_horizontal = ("university_directions",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name_ru",
        "id",
    )


@admin.register(Directions)
class DirectionsAdmin(admin.ModelAdmin):
    pass
