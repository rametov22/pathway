from modeltranslation.translator import register, TranslationOptions
from .models import FAQModel


@register(FAQModel)
class FAQTranslationOptions(TranslationOptions):
    fields = (
        "question",
        "answer",
    )
