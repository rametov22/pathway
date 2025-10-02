from modeltranslation.translator import register, TranslationOptions
from .models import Service, DayOfWeeks, ConsultationServices, EducationLevels


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "short_description",
        "description",
    )


@register(DayOfWeeks)
class DayOfWeeksTranslationOptions(TranslationOptions):
    fields = ("week",)


@register(ConsultationServices)
class ConsultationServicesTranslationOptions(TranslationOptions):
    fields = ("service",)


@register(EducationLevels)
class DEducationLevelsTranslationOptions(TranslationOptions):
    fields = ("level",)
