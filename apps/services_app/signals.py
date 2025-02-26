from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync

from apps.accounts_app.models import ApplicationDocument

from .models import ConsultationRequest, ServiceApplication


@receiver(post_save, sender=ServiceApplication)
def notify_admin_on_new_application(sender, instance, created, **kwargs):
    """Отправляет уведомление в Телеграм при новой заявке"""

    if created:
        from apps.services_app.telegram_bot import send_application_notification

        async_to_sync(send_application_notification)(instance)


@receiver(post_save, sender=ApplicationDocument)
def notify_admin_on_document_application_upload(sender, instance, created, **kwargs):
    if created:
        from apps.services_app.telegram_bot import (
            send_application_document_notification,
        )

        instance.application.default_application
        async_to_sync(send_application_document_notification)(instance)


@receiver(post_save, sender=ConsultationRequest)
def notify_admin_on_new_consultation(sender, instance, created, **kwargs):
    """Отправляет уведомление в Телеграм при новой заявке на консультацию"""
    if created:
        from apps.services_app.telegram_bot import send_consultation_notification

        async_to_sync(send_consultation_notification)(instance)


@receiver(post_save, sender=ServiceApplication)
def notify_user_on_status_change(sender, instance, **kwargs):
    """Отправляет уведомление пользователю, если статус заявки изменился"""
    if instance.pk:
        from apps.services_app.telegram_bot import create_user_notification

        try:
            user = instance.user
            service_name = instance.service.title

            status_messages = {
                "approved": f"✅ Ваша заявка '{service_name}' одобрена!",
                "rejected": f"❌ Ваша заявка '{service_name}' отклонена.",
                "in_progress": f"🔄 Ваша заявка '{service_name}' находится в обработке.",
                "pending": f"⏳ Ваша заявка '{service_name}' на рассмотрении.",
            }

            status_description = {
                "approved": "Теперь вы можете продолжить процесс.",
                "rejected": "Попробуйте еще раз или свяжитесь с поддержкой.",
                "in_progress": "Ожидайте, скоро с вами свяжется специалист.",
                "pending": "Администратор скоро рассмотрит вашу заявку.",
            }

            title = status_messages.get(instance.status, "📢 Обновление заявки")
            body = status_description.get(instance.status, "")

            async_to_sync(create_user_notification)(user, title, body)

        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=ConsultationRequest)
def notify_user_on_consultation_status_change(sender, instance, **kwargs):
    """Отправляет уведомление пользователю, если статус консультации изменился"""
    if instance.pk:
        from apps.services_app.telegram_bot import create_user_notification

        try:
            user = instance.user

            status_messages = {
                "in_progress": "⏳ Ваша консультация скоро начнется!",
                "answered": "✅ Вам ответили на консультацию!",
            }

            status_description = {
                "in_progress": "Ожидайте, скоро с вами свяжется специалист.",
                "answered": "Администратор ответил на ваш вопрос. Проверьте почту или чат.",
            }

            title = status_messages.get(instance.status, "📢 Обновление консультации")
            body = status_description.get(instance.status, "")

            async_to_sync(create_user_notification)(user, title, body)

        except sender.DoesNotExist:
            pass
