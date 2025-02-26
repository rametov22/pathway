from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import News, Notification


@receiver(post_save, sender=News)
def create_notification_for_news(sender, instance, created, **kwargs):
    if created and instance.show_news:
        Notification.objects.create(news=instance)


@receiver(post_delete, sender=News)
def delete_notification_for_news(sender, instance, **kwargs):
    Notification.objects.filter(news=instance).delete()
