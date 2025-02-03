from django.db import models
from mdeditor.fields import MDTextField


class Expert(models.Model):
    img = models.ImageField(upload_to="expert/")
    name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=20)
    job = models.CharField(max_length=256, verbose_name="Кем работает")
    expert_about = MDTextField()

    def __str__(self):
        return self.name
