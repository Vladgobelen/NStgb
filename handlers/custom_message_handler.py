from handlers.base import BaseHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class CustomMessageHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        if not await self.check_access(update):
            return

        text = update.message.text

        # Пропускаем обработку если это кнопка
        if text in ["📨 Сообщение в чат", "Назад"]:
            return

        try:
            if text.startswith("!сообщение:"):
                parts = text.split(maxsplit=1)
                if len(parts) < 2:
                    await update.message.reply_text(
                        "Использование: !сообщение: ваш текст",
                        reply_markup=ReplyKeyboardMarkup(
                            [["Назад"]], resize_keyboard=True
                        ),
                    )
                    return

                message = parts[1]
                formatted_message = (
                    f"/g ТГ: {update.message.from_user.first_name}: {message}"
                )

                if self.wow_service.send_to_wow(formatted_message):
                    await update.message.reply_text(
                        "✉️ Сообщение отправлено в игровой чат",
                        reply_markup=ReplyKeyboardMarkup(
                            [["Назад"]], resize_keyboard=True
                        ),
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Не удалось отправить сообщение",
                        reply_markup=ReplyKeyboardMarkup(
                            [["Назад"]], resize_keyboard=True
                        ),
                    )

        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Ошибка при отправке сообщения",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
