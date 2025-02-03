from django.db import models
from django.conf import settings
from mdeditor.fields import MDTextField


class Service(models.Model):
    title = models.CharField(max_length=256)
    short_description = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = MDTextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class ConsultationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
