# handlers/reload_handler.py
from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import asyncio
import logging

logger = logging.getLogger(__name__)


class ReloadHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '-релоэд'"""
        try:
            # Проверяем точное соответствие команде (без учёта регистра)
            if update.message.text.strip().lower() != "-релоэд":
                return

            msg = await update.message.reply_text("🔄 Выполняю перезагрузку аддонов...")

            # Выполняем команду перезагрузки в WoW
            success = self.wow_service.reload_addons()

            # Ждём 50 секунд
            await asyncio.sleep(50)

            if success:
                await msg.edit_text("✅ Аддоны перезагружены")
            else:
                await msg.edit_text("⚠️ Не удалось выполнить перезагрузку")

        except Exception as e:
            logger.error(f"Ошибка в ReloadHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Критическая ошибка при перезагрузке")
