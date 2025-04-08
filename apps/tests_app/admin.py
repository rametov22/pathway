from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import *


@admin.register(TestStart)
class TestStart(TabbedTranslationAdmin):
    list_display = (
        "title",
        "id",
    )


@admin.register(Test)
class TestAdmin(TabbedTranslationAdmin):
    list_display = ("title",)


@admin.register(TestQuestion)
class TestQuestionAdmin(TabbedTranslationAdmin):
    list_display = (
        "question",
        "test",
    )
    list_filter = ("test",)


@admin.register(TestAnswer)
class TestAnswerAdmin(TabbedTranslationAdmin):
    list_display = (
        "answer",
        "question",
    )
    list_filter = ("is_correct", "question__test", "question")


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "test", "correct_answers", "total_questions", "created_at")
    list_filter = ("test", "created_at")
    search_fields = ("user__username", "test__title")
    ordering = ("-created_at",)
