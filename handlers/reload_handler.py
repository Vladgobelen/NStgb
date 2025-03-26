from handlers.base import BaseHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class ReloadHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!релоэд' с поддержкой кнопок"""
        if not await self.check_access(update):
            return

        # Проверяем, что это команда релоад (кнопка или текст)
        text = update.message.text
        if not (text.lower() == "!релоэд" or text == "🔄 Обновление информации"):
            return

        try:
            await update.message.reply_text(
                "🔄 Пытаюсь обновить информацию...",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )

            if self.wow_service.reload_addons():
                await update.message.reply_text(
                    "✅ Информация успешно обновлена",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
            else:
                await update.message.reply_text(
                    "⚠️ Не удалось обновить информацию",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )

        except Exception as e:
            logger.error(f"Error in ReloadHandler: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Ошибка при обновлении информации",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
