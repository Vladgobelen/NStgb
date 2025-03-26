from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class GprlHandler:
    def __init__(self, wow_service, whitelist: set):
        self.wow_service = wow_service
        self.whitelist = whitelist

    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!гпрл'"""
        if update.effective_user.id not in self.whitelist:
            await update.message.reply_text("❌ Требуется подтверждение через /confirm")
            return

        # Проверяем точное соответствие команде
        if not update.message.text.lower() == "!гпрл":
            return

        try:
            await update.message.reply_text(
                "⚡ Отправляю команду обновления ГП...",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
            if self.wow_service.execute_gp_command():
                await update.message.reply_text(
                    "✅ Команда выполнена в игре",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
            else:
                await update.message.reply_text(
                    "⚠️ Не удалось выполнить команду",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )

        except Exception as e:
            logger.error(f"GPRL Error: {e}")
            await update.message.reply_text(
                "⚠️ Ошибка выполнения",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
