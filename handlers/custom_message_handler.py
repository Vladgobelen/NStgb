from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class CustomMessageHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команд типа '!сообщение:'"""
        if not await self.check_access(update):
            return

        try:
            parts = update.message.text.split(maxsplit=1)
            if len(parts) < 2:
                await update.message.reply_text("Использование: !сообщение: ваш текст")
                return

            message = parts[1]
            formatted_message = (
                f"/g ТГ: {update.message.from_user.first_name}: {message}"
            )

            if self.wow_service.send_to_wow(formatted_message):
                await update.message.reply_text("✉️ Сообщение отправлено в игровой чат")
            else:
                await update.message.reply_text("⚠️ Не удалось отправить сообщение")

        except Exception as e:
            logger.error(f"Error in CustomMessageHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при отправке сообщения")
