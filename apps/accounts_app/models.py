from datetime import timedelta
from django.utils.timezone import now
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    use_in_migrations = True
    """Custom manager for User model with email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email instead of a username."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        blank=True,
        null=True,
    )
    birth_date = models.DateField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    verification_code = models.CharField(max_length=6, blank=True, null=True)

    google_photo_url = models.URLField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email


class Question(models.Model):
    text = models.CharField(max_length=128, unique=True)
    is_multiple_answer = models.BooleanField(
        default=False, verbose_name="Можно выбрать несколько ответов"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вопрос для регистрации"
        verbose_name_plural = "Вопросы для регистрации"


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.text}"

    class Meta:
        verbose_name = "Ответ на вопрос для регистрации"
        verbose_name_plural = "Ответы на вопросы для регистрации"


class UserAnswer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="user_answers"
    )
    answers = models.ManyToManyField(Answer)

    def __str__(self):
        return f"{self.user.email} - {self.question.text}"

    class Meta:
        verbose_name = "Ответ пользователя при регистрации"
        verbose_name_plural = "Ответы пользователей при регистрации"


class DefaultApplication(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    deadline_days = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Дефолтная заявка для всех пользователей"
        verbose_name_plural = "Дефолтные заявки для всех пользователей"


class UserApplication(models.Model):

    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("in_progress", "В процессе"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    default_application = models.ForeignKey(
        DefaultApplication, on_delete=models.CASCADE, related_name="user_applications"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.deadline_date = now() + timedelta(
                days=self.default_application.deadline_days
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.default_application.title} ({self.get_status_display()}) - {self.user.email}"

    class Meta:
        verbose_name = "Статус Заявки пользователя"
        verbose_name_plural = "Статусы заявок пользователей"


class ApplicationDocument(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="application_documents",
    )
    application = models.ForeignKey(
        UserApplication, on_delete=models.CASCADE, related_name="documents"
    )
    file = models.FileField(upload_to="application_documents/")
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.application.default_application.title}) - {self.user.email}"

    class Meta:
        verbose_name = "Документ для заполнения заявки"
        verbose_name_plural = "Документы для заполнения заявок"


class UserDocument(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_documents",
    )
    file = models.FileField(upload_to="user_documents/")
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    class Meta:
        verbose_name = "Документ пользователя"
        verbose_name_plural = "Документы пользователей"
