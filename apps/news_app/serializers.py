from rest_framework import serializers
from .models import News, Notification, UserNotification, UserNotificationReadStatus


class NewsSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

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


class NotificationSerializer(serializers.ModelSerializer):
    id_news = serializers.IntegerField(source="news.id")
    title = serializers.CharField(source="news.news_title")
    category = serializers.CharField(source="news.category.category")
    image = serializers.ImageField(source="news.news_img")
    date = serializers.DateTimeField(source="news.date_added")
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "id_news", "title", "image", "category", "date", "is_read"]

    def get_is_read(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return UserNotificationReadStatus.objects.filter(
                user=request.user, notification=obj, is_read=True
            ).exists()


class UserNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserNotification
        fields = ["id", "title", "created_at", "is_read"]


class UserNotificationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserNotification
        fields = ["id", "title", "body", "created_at"]
