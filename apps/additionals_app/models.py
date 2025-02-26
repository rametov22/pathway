from django.db import models


class OurNetworks(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название соц сети")
    url = models.URLField()
    icon = models.ImageField(upload_to="social_icons/", blank=True, null=True)

    def __str__(self):
        return self.name


class FAQModel(models.Model):
    question = models.CharField(max_length=156)
    answer = models.TextField()

    def __str__(self):
        return self.question
