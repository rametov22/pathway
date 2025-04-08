from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import serializers
from urllib.parse import urljoin
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumbers import (
    parse,
    is_valid_number,
    format_number,
    PhoneNumberFormat,
    NumberParseException,
)
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
    user_application_status = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ("description", "user_application_status")

    def get_description(self, obj):
        request = self.context.get("request")
        if request:
            base_url = request.build_absolute_uri(settings.MEDIA_URL)
        else:
            base_url = settings.MEDIA_URL

        def add_base_url_to_images(text):
            import re

            pattern = r"(!\[.*?\]\()(/?media[\\/].*?)(\))"

            def replace_with_base_url(match):
                fixed_path = match.group(2).replace("\\", "/")
                fixed_path = re.sub(r"^media/", "", fixed_path)
                full_url = urljoin(base_url, fixed_path)
                return f"{match.group(1)}{full_url}{match.group(3)}"

            return re.sub(pattern, replace_with_base_url, text)

        return add_base_url_to_images(obj.description)

    def get_user_application_status(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            application = ServiceApplication.objects.filter(
                user=request.user, service=obj
            ).first()
            if application:
                return application.status
        return None


class ConsultationRequestSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(
        required=False, allow_blank=True, max_length=10
    )
    phone_number = serializers.CharField(
        required=False, allow_blank=True, max_length=20
    )
    name = serializers.CharField(required=False, allow_blank=True, max_length=256)
    country = serializers.CharField(required=False, allow_blank=True, max_length=10)
    question = serializers.CharField(required=True, max_length=512)

    class Meta:
        model = ConsultationRequest
        fields = ["country_code", "phone_number", "name", "country", "question"]

    def validate(self, data):
        user = self.context["request"].user
        is_authenticated = user.is_authenticated

        if not is_authenticated:
            if not data.get("name"):
                raise serializers.ValidationError({"name": _("Это поле обязательно.")})
            if not data.get("phone_number"):
                raise serializers.ValidationError(
                    {"phone_number": _("Это поле обязательно.")}
                )
            if not data.get("country_code"):
                raise serializers.ValidationError(
                    {"country_code": _("Это поле обьязательно")}
                )
            if not data.get("country"):
                raise serializers.ValidationError(
                    {"country": _("Это поле обьязательно")}
                )

        if "phone_number" in data and data["phone_number"]:
            if not data.get("country_code"):
                raise serializers.ValidationError(
                    {
                        "country_code": _(
                            "Это поле обязательно при вводе номера телефона."
                        )
                    }
                )
            if not data.get("country"):
                raise serializers.ValidationError(
                    {"country": _("Это поле обязательно при вводе номера телефона.")}
                )

            full_phone_number = f"{data['country_code']}{data['phone_number']}"

            try:
                parsed_phone = parse(full_phone_number, None)
                if not is_valid_number(parsed_phone):
                    raise serializers.ValidationError(
                        {"phone_number": _("Неверный номер телефона.")}
                    )
                data["phone_number"] = format_number(
                    parsed_phone, PhoneNumberFormat.E164
                )
            except NumberParseException:
                raise serializers.ValidationError(
                    {"phone_number": _("Неверный номер телефона.")}
                )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        is_authenticated = user.is_authenticated

        if is_authenticated:
            validated_data["user"] = user
            validated_data["full_name"] = validated_data.get(
                "name", user.get_full_name()
            )
            validated_data["phone_number"] = validated_data.get(
                "phone_number",
                user.phone_number if hasattr(user, "phone_number") else user.email,
            )
            validated_data["date_of_birth"] = getattr(user, "birth_date", None)
        else:
            validated_data["full_name"] = validated_data.pop("name")
            validated_data["date_of_birth"] = None

        validated_data.pop("country_code", None)
        validated_data.pop("country", None)
        validated_data.pop("name", None)

        if "question" not in validated_data:
            validated_data["question"] = ""

        consultation_request = super().create(validated_data)

        return {
            "phone_number": validated_data["phone_number"],
            "country": self.context["request"].data.get("country", ""),
            "question": validated_data["question"],
        }
