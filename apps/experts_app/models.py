from django.db import models
from mdeditor.fields import MDTextField
from apps.universities_app.models import Universities


class Expert(models.Model):
    img = models.ImageField(upload_to="expert/")
    name = models.CharField(max_length=256)
    telegram_url = models.URLField(default="https://t.me/")
    job = models.CharField(max_length=256, verbose_name="Кем работает")
    expert_about = MDTextField()

    def __str__(self):
        return self.name


class SuccessStories(models.Model):
    img = models.ImageField(upload_to="stories_success/")
    name = models.CharField(max_length=256)
    university = models.ForeignKey(
        Universities,
        on_delete=models.CASCADE,
        related_name="successes",
    )
    short_name_university = models.CharField(max_length=15)
    short_about = models.CharField(max_length=120)
    about = models.TextField()

    def __str__(self):
        return self.name
