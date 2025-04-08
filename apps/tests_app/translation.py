from modeltranslation.translator import register, TranslationOptions
from .models import TestStart, Test, TestQuestion, TestAnswer


@register(TestStart)
class TestStartTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
    )


@register(Test)
class TestTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(TestQuestion)
class TestQuestionTranslationOptions(TranslationOptions):
    fields = ("question",)


@register(TestAnswer)
class TestAnswerTranslationOptions(TranslationOptions):
    fields = ("answer",)
