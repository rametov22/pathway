from os import name
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Interest, User


class UserRegistrationSerializer(serializers.ModelSerializer):

    interests = serializers.ListField(child=serializers.IntegerField(), required=True)
    user_type = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={"min_length": "Password must be at least 8 characters long."},
    )

    class Meta:
        model = User
        fields = ["email", "password", "user_type", "interests"]

    def validate(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        interests_data = validated_data.pop("interests", [])

        user = User.objects.create(
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            user_type=validated_data["user_type"],
            is_active=False,
        )

        user.interests.set(interests_data)

        return {"user_id": user.id}


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    gender = serializers.ChoiceField(
        choices=[("Male", "Мужской"), ("Female", "Женский")], required=True
    )
    birth_date = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = ["name", "gender", "birth_date"]

    def update(self, instance, validated_data):
        missing_fields = []
        if "name" not in validated_data:
            missing_fields.append("name")
        if "gender" not in validated_data:
            missing_fields.append("gender")
        if "birth_date" not in validated_data:
            missing_fields.append("birth_date")

        if missing_fields:
            raise serializers.ValidationError(
                {field: ["Это поле обязательно."] for field in missing_fields}
            )

        full_name = validated_data.get("name", "").strip()
        name_parts = full_name.split(maxsplit=1)
        instance.first_name = name_parts[0] if name_parts else ""
        instance.last_name = name_parts[1] if len(name_parts) > 1 else ""
        instance.gender = validated_data.get("gender", instance.gender)
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.is_active = True
        instance.save()

        refresh = RefreshToken.for_user(instance)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        return instance, tokens


class RegistrationOptionsSerializer(serializers.Serializer):
    user_types = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()

    def get_user_types(self, obj):
        return [
            {"value": choice[0], "label": choice[1]}
            for choice in User._meta.get_field("user_type").choices
        ]

    def get_interests(self, obj):
        return [
            {"id": interest.id, "name": interest.name}
            for interest in Interest.objects.all()
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={"min_length": "Password must be at least 8 characters long."},
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid password")

        if not user.is_active:
            raise serializers.ValidationError("Your account is not active")

        refresh = RefreshToken.for_user(user)

        return {
            "user_id": user.id,
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "profile_picture",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "profile_picture",
            "first_name",
            "last_name",
            "name",
            "email",
            "phone_number",
            "birth_date",
            "gender",
            "country",
        )
        read_only_fields = (
            "email",
            "first_name",
            "last_name",
        )

    def update(self, instance, validated_data):
        name = validated_data.pop("name", None)

        if name:
            name_parts = name.strip().split(maxsplit=1)
            instance.first_name = name_parts[0] if name_parts else None
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ""

        profile_picture = validated_data.get("profile_picture")
        if profile_picture:
            instance.profile_picture = profile_picture

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
