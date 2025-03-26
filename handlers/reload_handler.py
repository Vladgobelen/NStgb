from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class ReloadHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!релоэд'"""
        if not await self.check_access(update):
            return

        # Проверяем точное соответствие команде
        if not update.message.text.strip().lower() == "!релоэд":
            return

        try:
            await update.message.reply_text(
                "🔄 Пытаюсь выполнить перезагрузку данных..."
            )

            # Выполняем команду через сервис
            success = self.wow_service.reload_addons()

            if success:
                await update.message.reply_text(
                    "✅ Перезагрузка данных успешно выполнена"
                )
            else:
                await update.message.reply_text(
                    "⚠️ Не удалось выполнить перезагрузку данных. Проверьте логи."
                )

        except Exception as e:
            logger.error(f"Ошибка в ReloadHandler: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Критическая ошибка при выполнении перезагрузки"
            )
