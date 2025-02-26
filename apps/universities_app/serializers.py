from django.db.models.functions import Coalesce
from django.conf import settings
from django.db.models import F
from rest_framework import serializers
from .models import Universities, Country


# UNIVERSITIES
class UniversitiesSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source="country.name_en")
    university_img = serializers.SerializerMethodField()

    class Meta:
        model = Universities
        fields = (
            "id",
            "university_name",
            "country",
            "year_of_study",
            "university_img",
        )

    def get_university_img(self, obj):
        request = self.context.get("request")
        if obj.university_img:
            return (
                request.build_absolute_uri(obj.university_img.url)
                if request
                else settings.MEDIA_URL + obj.university_img.url
            )
        return None


class UniversitiesDetailSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    city_with_country = serializers.SerializerMethodField()
    number_of_grants = serializers.SerializerMethodField()

    class Meta:
        model = Universities
        fields = (
            "university_img",
            "university_name",
            "country",
            "year_of_study",
            "city_with_country",
            "year_founded",
            "students_count",
            "international_students_count",
            "number_of_grants",
            "rating_qs",
            "rating_the",
            "history_university",
        )

    def get_country(self, obj):
        return obj.country.name_en

    def get_city_with_country(self, obj):
        return f"{obj.city}, {obj.country.name_ru}"

    def get_number_of_grants(self, obj):
        try:
            total_students = obj.students_count + obj.international_students_count
            if total_students > 0:
                percentage = (20 / 100) * total_students
                return f"20% - {round(percentage)}"
            else:
                return "0%"
        except (TypeError, ValueError):
            return "Invalid data"


# COUNTRIES
class CountrySerializer(serializers.ModelSerializer):
    universities_count = serializers.IntegerField()

    class Meta:
        model = Country
        fields = (
            "id",
            "country_img",
            "name_ru",
            "universities_count",
        )


class CountryDetailSerializer(serializers.ModelSerializer):
    universities = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = (
            "id",
            "name_ru",
            "country_img",
            "about_universities",
            "universities",
            "advantages_universities",
        )

    def get_universities(self, obj):
        top_universities = obj.universities.annotate(
            ranking_qs=Coalesce(F("rating_qs"), 9999),
            ranking_the=Coalesce(F("rating_the"), 9999),
        ).order_by("rating_qs", "rating_the")[:4]

        return UniversitiesSerializer(
            top_universities, many=True, context=self.context
        ).data
