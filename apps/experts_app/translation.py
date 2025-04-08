from modeltranslation.translator import register, TranslationOptions
from .models import SuccessStories, Expert


@register(Expert)
class ExpertTranslationOptions(TranslationOptions):
    fields = (
        "job",
        "expert_about",
    )


@register(SuccessStories)
class SuccessStoriesTranslationOptions(TranslationOptions):
    fields = (
        "short_about",
        "about",
    )
