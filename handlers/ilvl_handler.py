from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class IlvlHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды 'илвл'"""
        if not await self.check_access(update):
            return

        try:
            data = self.file_service.load_lua_file("ilvl")
            if not data or "Шеф" not in data or "илвл" not in data["Шеф"]:
                await update.message.reply_text("Данные не найдены")
                return

            await update.message.reply_text(
                f"🔹 Уровень предметов: {data['Шеф']['илвл']}"
            )
        except Exception as e:
            logger.error(f"Error in IlvlHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка обработки запроса")
