from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class GprlHandler:
    def __init__(self, wow_service):
        self.wow_service = wow_service

    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик ТОЛЬКО команды '!гпрл'"""
        try:
            # Точное сравнение команды (регистронезависимо)
            if update.message.text.strip().lower() != "!гпрл":
                return

            await update.message.reply_text("⚡ Выполняю gpEnTg() в игре...")
            if self.wow_service.execute_gp_command():
                await update.message.reply_text("✅ Команда выполнена")
            else:
                await update.message.reply_text("⚠️ Ошибка выполнения")

        except Exception as e:
            logger.error(f"GPRL Error: {e}")
            await update.message.reply_text("⚠️ Ошибка выполнения команды")
