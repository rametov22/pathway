from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    date_added = serializers.DateField(format=("%d-%m-%Y"))

    class Meta:
        model = News
        fields = (
            "id",
            "news_img",
            "category",
            "news_title",
            "news_about",
            "date_added",
        )

    def get_category(self, obj):
        return obj.category.category


class NewsDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    date_added = serializers.DateField(format=("%d-%m-%Y"))

    class Meta:
        model = News
        fields = (
            "news_img",
            "category",
            "news_title",
            "news_about",
            "date_added",
            "news_description",
        )

    def get_category(self, obj):
        return obj.category.category
