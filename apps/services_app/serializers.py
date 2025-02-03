from rest_framework import serializers

from .models import *


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = (
            "id",
            "title",
            "short_description",
            "price",
        )


class ServiceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ("description",)


class ConsultationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationRequest
        fields = ["phone_number"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        validated_data["full_name"] = user.get_full_name()
        validated_data["date_of_birth"] = user.birth_date
        return super().create(validated_data)
