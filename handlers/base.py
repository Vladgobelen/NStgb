from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class BaseHandler:
    def __init__(self, file_service=None, wow_service=None):
        self.file_service = file_service
        self.wow_service = wow_service

    async def handle(self, update: Update, context: CallbackContext):
        raise NotImplementedError("Метод handle должен быть реализован в подклассах")
