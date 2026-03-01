from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext


class AddonHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды -аддон"""
        message = "🔗 Скачать аддон: https://github.com/Vladgobelen/NSQCuE/releases/download/v1.0.2/NSQCuE.exe"
        await update.message.reply_text(message)
