from django.contrib import admin

from .models import Expert, SuccessStories


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    pass


@admin.register(SuccessStories)
class SuccessStories(admin.ModelAdmin):
    pass
