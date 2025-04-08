from modeltranslation.translator import register, TranslationOptions
from .models import Category, News


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("category",)


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = (
        "news_title",
        "news_about",
        "news_description",
    )
