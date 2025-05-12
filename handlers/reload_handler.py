from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class ReloadHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!релоэд'"""
        try:
            # Проверяем точное соответствие команде
            if update.message.text.strip().lower() != "!релоэд":
                return

            await update.message.reply_text("🔄 Выполняю перезагрузку аддонов...")

            if self.wow_service.reload_addons():
                await update.message.reply_text("✅ Аддоны перезагружены")
            else:
                await update.message.reply_text("⚠️ Не удалось выполнить перезагрузку")

        except Exception as e:
            logger.error(f"Ошибка в ReloadHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Критическая ошибка при перезагрузке")
