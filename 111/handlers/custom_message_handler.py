from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class CustomMessageHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        try:
            parts = update.message.text.split(maxsplit=1)
            if len(parts) < 2:
                await update.message.reply_text("Использование: !сообщение: ваш текст")
                return

            message = parts[1]
            if self.wow_service.send_to_wow(f"/g ТГ: {message}"):
                await update.message.reply_text("✉️ Сообщение отправлено")
            else:
                await update.message.reply_text("⚠️ Ошибка отправки")
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await update.message.reply_text("⚠️ Ошибка выполнения")
