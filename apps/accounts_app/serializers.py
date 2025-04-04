import os
import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django_countries.serializers import CountryFieldMixin
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField

from Inconnect.core import PyInconnect

from .models import (
    Answer,
    ApplicationDocument,
    Question,
    User,
    UserAnswer,
    UserApplication,
    UserDocument,
)
from .validators.file_size import validate_file_size


mail_client = PyInconnect(api_key=settings.API_KEY_SMTP)


class RegisterStep1Serializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={"min_length": "Password must be at least 8 characters long."},
    )
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def validate(self, data):
        existing_user = User.objects.filter(email=data["email"]).first()

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Пароли на совпадают."}
            )

        if existing_user and existing_user.is_active:
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        email = validated_data["email"]

        User.objects.filter(email=email, is_active=False).delete()

        verification_code = str(random.randint(100000, 999999))
        user = User.objects.create(
            email=email,
            password=make_password(validated_data["password"]),
            is_active=False,
            verification_code=verification_code,
        )

        mail_client.send_email(
            name="pathway",
            from_email="info@pthwy.co",
            to_email=user.email,
            subject="Восстановление пароля",
            message=f"Ваш код для восстановления пароля: {verification_code}",
        )
        return user


class VerifyCodeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        user = User.objects.filter(id=data["user_id"]).first()
        if not user:
            raise serializers.ValidationError({"user_id": "Пользователь не найден."})
        if user.verification_code != data["code"]:
            raise serializers.ValidationError({"code": "Неверный код."})
        return data

    def save(self):
        user = User.objects.get(id=self.validated_data["user_id"])
        user.verification_code = None
        user.save()
        return {"message": "Код подтвержден.", "user_id": user.id}


class CompleteProfileSerializer(serializers.ModelSerializer):
    GENDER_CHOICES = [("Male", "Мужской"), ("Female", "Женский")]

    name = serializers.CharField(required=True, write_only=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    birth_date = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "name", "gender", "birth_date"]
        read_only_fields = ["first_name", "last_name"]

    def validate(self, data):
        if not data.get("name"):
            raise serializers.ValidationError({"name": "Это поле обязательно."})
        if not data.get("gender"):
            raise serializers.ValidationError({"gender": "Это поле обязательно."})
        if not data.get("birth_date"):
            raise serializers.ValidationError({"birth_date": "Это поле обязательно."})
        return data

    def update(self, instance, validated_data):
        name = validated_data.pop("name", None)
        if name:
            name_parts = name.strip().split(maxsplit=1)
            instance.first_name = name_parts[0] if name_parts else ""
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ""

        instance.gender = validated_data.get("gender", instance.gender)
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.save()
        return instance


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "is_multiple_answer", "answers"]

    def get_answers(self, obj):
        return [
            {
                "id": answer.id,
                "text": answer.text,
            }
            for answer in obj.answers.all()
        ]


class UserAnswerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(), required=True, allow_empty=False
        ),
        required=True,
    )

    def validate(self, data):
        user_id = data["user_id"]
        answers = data["answers"]

        user = User.objects.filter(id=user_id).first()
        if not user:
            raise serializers.ValidationError({"user_id": "Пользователь не найден"})

        for question_id, answer_ids in answers.items():
            question = Question.objects.filter(id=question_id).first()
            if not question:
                raise serializers.ValidationError(
                    {f"question_{question_id}": "Такого вопроса не существует"}
                )

            for answer_id in answer_ids:
                answer = Answer.objects.filter(id=answer_id, question=question).first()
                if not answer:
                    raise serializers.ValidationError(
                        {
                            f"answer_{answer_id}": f"Ответ {answer_id} не принадлежит вопросу {question_id}"
                        }
                    )
        return data

    def save(self):
        user = User.objects.get(id=self.validated_data["user_id"])
        answers = self.validated_data["answers"]

        for question_id, answer_ids in answers.items():
            question = Question.objects.get(id=question_id)
            user_answer, created = UserAnswer.objects.get_or_create(
                user=user, question=question
            )
            user_answer.answers.set(Answer.objects.filter(id__in=answer_ids))

        if UserAnswer.objects.filter(user=user).count() == Question.objects.count():
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return {
                "message": "Регистрация заверщена.",
                "access_token": str(refresh.access_token),
                "refresh": str(refresh),
            }

        return {"message": "Ответы сохранены."}


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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email не найден."}
            )
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        verification_code = str(random.randint(100000, 999999))
        user.verification_code = verification_code
        user.save()

        mail_client.send_email(
            name="pathway",
            from_email="info@pthwy.co",
            to_email=user.email,
            subject="Восстановление пароля",
            message=f"Ваш код для восстановления пароля: {verification_code}",
        )

        return {
            "message": "Код востановления отправлен на почту.",
            "email": user.email,
        }


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)

    def validate(self, data):
        email = data["email"]
        code = data["code"]
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": "Пользователь не найден"})
        if user.verification_code != code:
            raise serializers.ValidationError({"code": "Код не совпадает"})
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.verification_code = None
        user.save()
        return {
            "message": "Код подтвержден, установите новый пароль.",
            "email": user.email,
        }


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, required=True
    )

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Пароли не совпадают."}
            )
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.password = make_password(self.validated_data["password"])
        user.save()
        return {"message": "Пароль успешно изменен. Теперь вы можете войти в аккаунт."}


# PROFILE
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "profile_picture",
        )


class ProfileUpdateSerializer(CountryFieldMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    phone_number = PhoneNumberField(required=False, max_length=20)
    # country_code = serializers.CharField(
    #     required=False, allow_blank=True, max_length=10
    # )
    # country = serializers.CharField(required=False, allow_blank=True, max_length=10)

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


class ProfileDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    file = serializers.FileField()
    size = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()

    def get_size(self, obj):
        if obj.file:
            size_in_bytes = obj.file.size
            if size_in_bytes < 1024:
                return f"{size_in_bytes} B"
            elif size_in_bytes < 1024 * 1024:
                return f"{size_in_bytes / 1024:.0f} KB"
            else:
                return f"{size_in_bytes / (1024 * 1024):.0f} MB"
        return None

    def get_format(self, obj):
        if obj.file:
            return obj.file.name.split(".")[-1]
        return None

    class Meta:
        fields = ["id", "title", "file", "size", "format"]


# DOCUMENTS
class ApplicationDocumentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    format = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationDocument
        fields = ["title", "file", "size", "format"]

    def get_file(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def get_size(self, obj):
        if obj.file:
            size_in_bytes = obj.file.size
            if size_in_bytes < 1024:
                return f"{size_in_bytes} B"
            elif size_in_bytes < 1024 * 1024:
                return f"{size_in_bytes / 1024:.0f} KB"
            else:
                return f"{size_in_bytes / (1024 * 1024):.0f} MB"
        return None

    def get_format(self, obj):
        if obj.file:
            return obj.file.name.split(".")[-1]
        return None


class UserApplicationSerializer(serializers.ModelSerializer):
    default_application_title = serializers.CharField(
        source="default_application.title"
    )
    documents = ApplicationDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = UserApplication
        fields = [
            "id",
            "default_application_title",
            "status",
            "deadline_date",
            "documents",
        ]


class ApplicationDocumentUploadSerializer(serializers.ModelSerializer):
    application_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(validators=[validate_file_size])

    class Meta:
        model = ApplicationDocument
        fields = ["id", "title", "file", "uploaded_at", "application_id"]
        read_only_fields = ["uploaded_at"]

    def create(self, validated_data):
        application_id = validated_data.pop("application_id")
        application = UserApplication.objects.get(id=application_id)

        if application.status in ["in_progress", "approved"]:
            raise serializers.ValidationError(
                f"Нельзя загружать файлы для этой заявки. вы уже загрузили, status: {application.status}"
            )

        application.status = "in_progress"
        application.save()

        file = validated_data.get("file")
        filename_without_extension = (
            os.path.splitext(file.name)[0] if file else "Untitled"
        )

        document = ApplicationDocument.objects.create(
            application=application, title=filename_without_extension, **validated_data
        )
        return document


class UserDocumentUploadSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    file = serializers.FileField(validators=[validate_file_size])

    class Meta:
        model = UserDocument
        fields = ["id", "title", "file", "uploaded_at"]

    def create(self, validated_data):
        file = validated_data.get("file")
        filename_without_extension = (
            os.path.splitext(file.name)[0] if file else "Untitled"
        )

        document = UserDocument.objects.create(
            title=filename_without_extension, **validated_data
        )
        return document


class CountrySerializerAccounts(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
