from modeltranslation.translator import register, TranslationOptions
from .models import Directions, Universities, Country


@register(Universities)
class UniversitiesTranslationOptions(TranslationOptions):
    fields = (
        "city",
        "history_university",
    )


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "about_universities",
        "advantages_universities",
    )


@register(Directions)
class DirectionTranslationOptions(TranslationOptions):
    fields = ("direction",)
