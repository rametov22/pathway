from io import BytesIO
import os
import django
import logging
from django.utils.timezone import now
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from asgiref.sync import sync_to_async
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    Application,
    ContextTypes,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.services_app.models import ServiceApplication, ConsultationRequest
from apps.accounts_app.models import ApplicationDocument
from apps.news_app.models import UserNotification

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_ADMIN_CHAT_ID = settings.TELEGRAM_ADMIN_CHAT_ID
TELEGRAM_GROUP_CHAT_ID = settings.TELEGRAM_GROUP_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_user_notification(user, title, body):
    """Создает уведомление для пользователя"""
    await sync_to_async(UserNotification.objects.create)(
        user=user, title=title, body=body
    )


#
async def send_application_notification(application):
    """Отправляет заявку админу в Телеграм"""

    message_text = (
        f"📢 Новая заявка на сервис!\n\n"
        f"👤 Пользователь: {application.user.email}\n"
        f"🔹 Сервис: {application.service.title}\n"
        f"📅 Дата заявки: {application.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Одобрить", callback_data=f"approve_{application.id}"
            ),
            InlineKeyboardButton(
                "❌ Отклонить", callback_data=f"reject_{application.id}"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    await application.bot.send_message(
        chat_id=TELEGRAM_GROUP_CHAT_ID, text=message_text, reply_markup=reply_markup
    )


async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатие кнопок"""

    query = update.callback_query
    await query.answer()

    action, app_id = query.data.split("_")
    app_id = int(app_id)

    admin_name = query.from_user.full_name
    admin_username = query.from_user.username

    try:
        application = await sync_to_async(
            lambda: ServiceApplication.objects.select_related("service").get(id=app_id)
        )()
    except ServiceApplication.DoesNotExist:
        await query.edit_message_text(text="❌ Заявка уже не существует.")
        return

    service_title = await sync_to_async(lambda: application.service.title)()
    service_user = await sync_to_async(lambda: application.user)()

    admin_info = (
        f"👤 {admin_name} (@{admin_username})" if admin_username else f"👤 {admin_name}"
    )

    if action == "approve":
        await sync_to_async(lambda: setattr(application, "status", "approved"))()
        await sync_to_async(application.save)()

        await query.edit_message_text(
            text=f"✅ Заявка на **{service_title}** одобрена для пользователя {service_user}!\n\n"
            f"👤 Одобрил: {admin_info}"
        )

    elif action == "reject":
        await sync_to_async(lambda: setattr(application, "status", "rejected"))()
        await sync_to_async(application.save)()
        
        await query.edit_message_text(
            text=f"❌ Заявка на **{service_title}** отклонена для пользователя {service_user}!\n\n"
            f"👤 Отклонил: {admin_info}"
        )


#
async def send_application_document_notification(document):
    """Отправляет документ в Telegram для проверки"""

    application = await sync_to_async(lambda: document.application)()
    application_title = await sync_to_async(
        lambda: application.default_application.title
    )()
    user_email = await sync_to_async(lambda: document.user.email)()

    message_text = (
        f"📑 *Новый документ загружен!*\n\n"
        f"👤 *Пользователь:* {user_email}\n"
        f"📄 *Файл:* {document.title}\n"
        f"📝 *Заявка:* {application_title}\n"
        f"📅 *Дата загрузки:* {document.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Одобрить", callback_data=f"approve_doc_{document.id}"
            ),
            InlineKeyboardButton(
                "❌ Отклонить", callback_data=f"reject_doc_{document.id}"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    file_path = document.file.path
    with open(file_path, "rb") as file:
        file_data = BytesIO(file.read())
        file_data.name = os.path.basename(file_path)

        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        await application.bot.send_document(
            chat_id=TELEGRAM_GROUP_CHAT_ID,
            document=InputFile(file_data),
            caption=message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


async def handle_document_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    action = f"{parts[0]}_{parts[1]}"
    document_id = int(parts[2])

    admin_name = query.from_user.full_name
    admin_username = query.from_user.username

    document = await sync_to_async(
        lambda: ApplicationDocument.objects.filter(id=document_id)
        .select_related("user", "application")
        .first()
    )()

    if not document:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Документ уже не существует.",
        )
        return

    user = await sync_to_async(lambda: document.user)()
    application = await sync_to_async(lambda: document.application)()
    application_title = await sync_to_async(
        lambda: application.default_application.title
    )()

    admin_info = (
        f"👤 {admin_name} (@{admin_username})" if admin_username else f"👤 {admin_name}"
    )

    if action == "approve_doc":
        await sync_to_async(lambda: setattr(application, "status", "approved"))()
        await sync_to_async(application.save)()

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ Документ одобрен, заявка подтверждена!\n\n"
            f"👤 Пользователь: {user.email}\n"
            f"📄 Файл: {document.title}\n"
            f"📝 Заявка: {application_title}\n"
            f"📅 Дата загрузки: {document.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"✅ Одобрил: {admin_info}",
        )

    elif action == "reject_doc":
        await sync_to_async(document.delete)()

        await sync_to_async(lambda: setattr(application, "status", "rejected"))()
        await sync_to_async(application.save)()

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ Документ отклонен и удален!\n\n"
            f"👤 Пользователь: {user.email}\n"
            f"📄 Файл: {document.title}\n"
            f"📝 Заявка: {application_title}\n"
            f"📅 Дата загрузки: {document.uploaded_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"🚨 Отклонил: {admin_info}",
        )

    await query.delete_message()


#
async def send_consultation_notification(consultation):
    """Отправляет уведомление админу в Телеграм о новой консультации"""

    message_text = (
        f"📢 Новая заявка на консультацию!\n\n"
        f"👤 Пользователь: {consultation.user.email}\n"
        f"📛 Имя: {consultation.full_name}\n"
        f"📞 Телефон: {consultation.phone_number}\n"
        f"📅 Дата рождения: {consultation.date_of_birth.strftime('%Y-%m-%d')}\n"
        f"❓ Вопрос: {consultation.question}\n"
        f"📅 Дата заявки: {consultation.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

    keyboard = [
        [InlineKeyboardButton("📩 Я отвечу", callback_data=f"take_{consultation.id}")],
        [
            InlineKeyboardButton(
                "✅ Отвечено", callback_data=f"answered_{consultation.id}"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    await application.bot.send_message(
        chat_id=TELEGRAM_GROUP_CHAT_ID,
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def handle_consultation_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    action, consultation_id = query.data.split("_")
    consultation_id = int(consultation_id)

    admin_name = query.from_user.full_name
    admin_username = query.from_user.username

    consultation = await sync_to_async(
        lambda: ConsultationRequest.objects.filter(id=consultation_id).first()
    )()

    if not consultation:
        await query.edit_message_text(text="❌ Заявка уже не существует.")
        return

    user = await sync_to_async(lambda: consultation.user)()
    admin_info = (
        f"👤 {admin_name} (@{admin_username})" if admin_username else f"👤 {admin_name}"
    )

    if action == "take":
        await sync_to_async(lambda: setattr(consultation, "status", "in_progress"))()
        await sync_to_async(consultation.save)()

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Отвечено", callback_data=f"answered_{consultation.id}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"📩 Заявка на консультацию\n\n"
            f"👤 Пользователь: {user.email}\n"
            f"📛 Имя: {consultation.full_name}\n"
            f"📞 Телефон: {consultation.phone_number}\n"
            f"📅 Дата рождения: {consultation.date_of_birth.strftime('%Y-%m-%d')}\n"
            f"❓ Вопрос: {consultation.question}\n"
            f"📅 Дата заявки: {consultation.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"✅ Ответит: {admin_info}",
            reply_markup=reply_markup,
        )

    elif action == "answered":
        await sync_to_async(lambda: setattr(consultation, "status", "answered"))()
        await sync_to_async(lambda: setattr(consultation, "answered_at", now()))()
        await sync_to_async(consultation.save)()

        answered_at = await sync_to_async(
            lambda: consultation.answered_at.strftime("%Y-%m-%d %H:%M")
        )()

        await query.edit_message_text(
            text=f"✅ Консультация завершена!\n\n"
            f"👤 Пользователь: {user.email}\n"
            f"📛 Имя: {consultation.full_name}\n"
            f"📞 Телефон: {consultation.phone_number}\n"
            f"📅 Дата рождения: {consultation.date_of_birth.strftime('%Y-%m-%d')}\n"
            f"❓ Вопрос: {consultation.question}\n"
            f"📅 Дата заявки: {consultation.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"📅 Дата ответа: {answered_at}\n\n"
            f"✅ Ответил: {admin_info}"
        )


#
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    await update.message.reply_text("Привет! Я бот для управления заявками в Django.")


def main():
    """Запускает бота"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        CallbackQueryHandler(handle_button_click, pattern="^(approve|reject)_\d+$")
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_consultation_button, pattern="^(take|answered)_\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_document_button, pattern="^(approve_doc|reject_doc)_\d+$"
        )
    )

    application.run_polling()
