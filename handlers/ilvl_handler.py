from handlers.base import BaseHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class IlvlHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды 'илвл' с поддержкой кнопок"""
        if not await self.check_access(update):
            return

        # Проверяем, что это команда ilvl (кнопка или текст)
        text = update.message.text
        if not (text.lower() == "илвл" or text == "📈 Уровень предметов"):
            return

        try:
            data = self.file_service.load_lua_file("ilvl")
            if not data or "Шеф" not in data or "илвл" not in data["Шеф"]:
                await update.message.reply_text(
                    "Данные не найдены",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
                return

            await update.message.reply_text(
                f"🔹 Уровень предметов: {data['Шеф']['илвл']}",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
        except Exception as e:
            logger.error(f"Error in IlvlHandler: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Ошибка обработки запроса",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
