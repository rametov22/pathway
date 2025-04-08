from datetime import timedelta
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from asgiref.sync import async_to_sync

from .models import ApplicationDocument, User, DefaultApplication, UserApplication


@receiver(post_save, sender=User)
def assign_default_applications_to_new_user(sender, instance, created, **kwargs):
    """Добавляем дефолтные заявки только ОДИН раз при создании нового пользователя"""
    if created:
        default_apps = DefaultApplication.objects.filter(is_active=True)
        for default_app in default_apps:
            if not UserApplication.objects.filter(
                user=instance, default_application=default_app
            ).exists():
                deadline = now() + timedelta(days=default_app.deadline_days)
                UserApplication.objects.create(
                    user=instance,
                    default_application=default_app,
                    deadline_date=deadline,
                )


@receiver(post_save, sender=DefaultApplication)
def assign_new_default_application_to_users(sender, instance, created, **kwargs):
    """При создании новой дефолтной заявки добавляем ее всем существующим пользователям"""
    if created:
        users = User.objects.all()
        for user in users:
            if not UserApplication.objects.filter(
                user=user, default_application=instance
            ).exists():
                deadline = now() + timedelta(days=instance.deadline_days)
                UserApplication.objects.create(
                    user=user, default_application=instance, deadline_date=deadline
                )


@receiver(post_save, sender=UserApplication)
def notify_user_on_application_status_change(sender, instance, **kwargs):
    """Отправляет уведомление пользователю, если статус заявки изменился"""
    if instance.pk:
        from apps.services_app.telegram_bot import create_user_notification

        try:
            user = instance.user
            application_name = instance.default_application.title

            status_messages = {
                "approved": f"✅ Ваша заявка '{application_name}' одобрена!",
                "rejected": f"❌ Ваша заявка '{application_name}' отклонена.",
                "in_progress": f"🔄 Ваша заявка '{application_name}' в процессе обработки.",
                "pending": f"⏳ Ваша заявка '{application_name}' на рассмотрении.",
            }

            status_description = {
                "approved": f"Теперь вы можете продолжить процесс по заявке '{application_name}'.",
                "rejected": f"Документы отклонены. Свяжитесь с поддержкой или попробуйте снова.",
                "in_progress": f"Ожидайте, скоро администратор рассмотрит вашу заявку.",
                "pending": f"Заявка принята, но пока не рассмотрена администратором.",
            }

            title = status_messages.get(instance.status, "📢 Обновление заявки")
            body = status_description.get(instance.status, "")

            async_to_sync(create_user_notification)(user, title, body)

        except sender.DoesNotExist:
            pass
