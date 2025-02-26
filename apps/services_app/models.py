from django.db import models
from django.conf import settings
from mdeditor.fields import MDTextField

from apps.experts_app.models import Expert


class Service(models.Model):
    title = models.CharField(max_length=256)
    short_description = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = MDTextField()
    created_at = models.DateField(auto_now_add=True)

    experts = models.ManyToManyField(Expert, related_name="services")

    def __str__(self):
        return self.title


class ServiceApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидание"),
        ("approved", "Одобрено"),
        ("rejected", "Отклонено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_applications",
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.service.title} ({self.get_status_display()})"


class ConsultationRequest(models.Model):
    STATUS_CHOICES = [
        ("not_answered", "Не отвечено"),
        ("in_progress", "Отвечают"),
        ("answered", "Отвечено"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    question = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_answered"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_name
