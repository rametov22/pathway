from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "id",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    search_fields = ("email",)
    list_filter = (
        "gender",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    ordering = (
        "-is_superuser",
        "-is_active",
        "-date_joined",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "gender",
                    "birth_date",
                    "country",
                    "profile_picture",
                )
            },
        ),
        (
            "Additional Info",
            {
                "fields": (
                    "verification_code",
                    "google_photo_url",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


# class CustomUserAdmin(UserAdmin):
#     model = User
#     list_display = ("email", "is_staff", "is_superuser")
#     ordering = ("email",)
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
#         (
#             "Personal Info",
#             {"fields": ("phone_number", "gender", "birth_date", "country")},
#         ),
#         ("Important dates", {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("email", "password1", "password2", "is_staff", "is_active"),
#             },
#         ),
#     )
#     search_fields = ("email",)
#     ordering = ("email",)


# admin.site.register(User, CustomUserAdmin)


@admin.register(Question)
class QuestionAdmin(TabbedTranslationAdmin):
    list_display = (
        "text",
        "id",
    )


@admin.register(Answer)
class AnswerAdmin(TabbedTranslationAdmin):
    list_display = (
        "question",
        "text",
        "id",
    )


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "question",
    )
    filter_horizontal = ("answers",)
    search_fields = ("user",)
    list_filter = ("question",)


@admin.register(DefaultApplication)
class DefaultApplicationAdmin(TabbedTranslationAdmin):
    list_display = (
        "title",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    readonly_fields = ("created_at",)


@admin.register(UserApplication)
class UserApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "default_application",
        "status",
        "id",
    )
    list_filter = (
        "status",
        "default_application",
    )
    search_fields = ("user__email",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "id",
        "title",
        "application__default_application",
        "uploaded_at",
    )
    readonly_fields = ("uploaded_at",)
    list_filter = ("application__default_application",)
    search_fields = ("user__email",)


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "id",
        "title",
        "uploaded_at",
    )
    readonly_fields = ("uploaded_at",)
    list_filter = ("uploaded_at",)
    search_fields = ("user__email",)
