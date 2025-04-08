from modeltranslation.translator import register, TranslationOptions
from .models import Question, Answer, DefaultApplication


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(Answer)
class AnswerTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(DefaultApplication)
class DefaultApplicationTranslationOptions(TranslationOptions):
    fields = ("title",)
