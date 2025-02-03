from django.contrib import admin
from .models import Category, News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass
