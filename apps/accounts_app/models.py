from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
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

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        blank=True,
        null=True,
    )
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    user_type = models.CharField(
        max_length=100,
        choices=[
            ("School Student", "Студент заканчивающий школу"),
            ("Undergraduate Student", "Студент заканчивающий бакалавриат"),
            ("Magistrature Student", "Студент заканчивающий магистратуру"),
            ("Graduate student", "Аспирант"),
            ("Professional", "Профессионал"),
        ],
        blank=True,
        null=True,
    )

    google_photo_url = models.URLField(max_length=200, null=True, blank=True)

    interests = models.ManyToManyField("Interest", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email


class Interest(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
