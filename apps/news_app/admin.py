from django.contrib import admin
from .models import (
    Category,
    News,
    Notification,
    UserNotification,
    UserNotificationReadStatus,
)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    readonly_fields = ("date_added",)


@admin.register(Category)
class Category(admin.ModelAdmin):
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
