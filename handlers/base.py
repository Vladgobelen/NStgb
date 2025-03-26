from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class BaseHandler:
    def __init__(self, file_service, wow_service, whitelist: set):
        self.file_service = file_service
        self.wow_service = wow_service
        self.whitelist = whitelist

    def is_user_confirmed(self, user_id: int) -> bool:
        """Проверка подтверждения пользователя"""
        return user_id in self.whitelist

    async def check_access(self, update: Update) -> bool:
        """Проверка доступа пользователя"""
        if not self.is_user_confirmed(update.effective_user.id):
            await update.message.reply_text("❌ Сначала подтвердитесь через /confirm")
            return False
        return True

    async def handle(self, update: Update, context: CallbackContext):
        """Основной метод обработки (должен быть переопределен)"""
        raise NotImplementedError
