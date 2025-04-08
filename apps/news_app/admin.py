from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import (
    Category,
    News,
    Notification,
    UserNotification,
    UserNotificationReadStatus,
)


@admin.register(News)
class NewsAdmin(TabbedTranslationAdmin):
    readonly_fields = ("date_added",)


@admin.register(Category)
class Category(TabbedTranslationAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "created_at",
        "is_read",
    )
    search_fields = ("user",)
    list_filter = (
        "created_at",
        "is_read",
    )
    readonly_fields = ("created_at",)


@admin.register(UserNotificationReadStatus)
class UserNotificationReadStatusAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "notification",
        "is_read",
    )
