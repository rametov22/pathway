import datetime
from django.db import models


class News(models.Model):
    news_img = models.ImageField(upload_to="news/")
    news_title = models.CharField(max_length=256)
    news_about = models.CharField(max_length=512, verbose_name="Кратко о новости")
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT, related_name="news"
    )
    date_added = models.DateField(
        default=datetime.date.today, verbose_name="Дата добавления"
    )
    news_description = models.TextField(verbose_name="Полное описание")
    show_news = models.BooleanField(default=True, verbose_name="Показывать новость")

    def __str__(self):
        return self.news_title


class Category(models.Model):
    category = models.CharField(max_length=256)

    def __str__(self):
        return self.category
