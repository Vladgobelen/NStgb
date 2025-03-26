from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class GprlHandler:
    def __init__(self, wow_service, whitelist: set):
        self.wow_service = wow_service
        self.whitelist = whitelist

    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!гпрл'"""
        try:
            # Проверка доступа
            if update.effective_user.id not in self.whitelist:
                await update.message.reply_text(
                    "❌ Требуется подтверждение через /confirm"
                )
                return

            # Проверяем точное соответствие команде (регистронезависимо)
            if not update.message.text.strip().lower() == "!гпрл":
                return

            # Выполнение команды
            await update.message.reply_text("⚡ Отправляю команду обновления GP...")
            if self.wow_service.execute_gp_command():
                await update.message.reply_text("✅ Команда выполнена в игре")
            else:
                await update.message.reply_text("⚠️ Не удалось выполнить команду")

        except Exception as e:
            logger.error(f"GPRL Error: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка выполнения")
