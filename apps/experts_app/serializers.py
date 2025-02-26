from rest_framework import serializers

from apps.services_app.models import ServiceApplication

from .models import Expert, SuccessStories


class ExpertsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expert
        fields = (
            "id",
            "img",
            "name",
            "job",
        )


class ExpertsDetailSerializer(serializers.ModelSerializer):
    telegram_url = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = (
            "img",
            "name",
            "job",
            "telegram_url",
            "expert_about",
        )

    def get_telegram_url(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user = request.user
            if ServiceApplication.objects.filter(
                user=user, service__experts=obj, status="approved"
            ).exists():
                return obj.telegram_url
        return None


class SuccessStoriesSerializer(serializers.ModelSerializer):
    university_img = serializers.ImageField(
        source="university.university_img", read_only=True
    )

    class Meta:
        model = SuccessStories
        fields = (
            "id",
            "img",
            "name",
            "short_name_university",
            "university_img",
            "short_about",
        )


class SuccessStoriesDetailSerializer(serializers.ModelSerializer):
    university_img = serializers.ImageField(source="university.university_img")

    class Meta:
        model = SuccessStories
        fields = (
            "img",
            "name",
            "short_name_university",
            "university_img",
            "about",
        )
