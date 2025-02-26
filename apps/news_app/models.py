from django.conf import settings
from django.db import models


class News(models.Model):
    news_img = models.ImageField(upload_to="news/")
    news_title = models.CharField(max_length=256)
    news_about = models.CharField(max_length=512, verbose_name="Кратко о новости")
    category = models.ForeignKey(
        "Category", on_delete=models.PROTECT, related_name="news"
    )
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    news_description = models.TextField(verbose_name="Полное описание")
    show_news = models.BooleanField(default=True, verbose_name="Показывать новость")

    def __str__(self):
        return self.news_title


class Category(models.Model):
    category = models.CharField(max_length=256)

    def __str__(self):
        return self.category


class Notification(models.Model):
    news = models.ForeignKey(
        News, on_delete=models.CASCADE, related_name="notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление: {self.news.news_title}"


class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.title} ({"Прочитано" if self.is_read else "не прочитано"})'


class UserNotificationReadStatus(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="read_notifications",
    )
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="read_by_users"
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.notification.news.news_title} ({"Прочитано" if self.is_read else "Не прочитано"})'
