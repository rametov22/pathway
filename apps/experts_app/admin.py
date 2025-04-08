from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import Expert, SuccessStories


@admin.register(Expert)
class ExpertAdmin(TabbedTranslationAdmin):
    pass


@admin.register(SuccessStories)
class SuccessStories(TabbedTranslationAdmin):
    pass
