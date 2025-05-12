import logging
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler as ExtMessageHandler,
    filters,
    CallbackContext,
)
from config import Config
from services.file_service import FileService
from services.wow_service import WowService
from handlers import (
    IlvlHandler,
    GpHandler,
    CustomMessageHandler,
    ReloadHandler,
    GprlHandler,
    ServerCheckHandler,
)

logger = logging.getLogger(__name__)


class WowBot:
    def __init__(self):
        self.config = Config()
        self.file_service = FileService(self.config.WOW_FILES)
        self.wow_service = WowService(self.config.WOW_COMMANDS)

        self.handlers = {
            "илвл": IlvlHandler(self.file_service, self.wow_service),
            "!гп": GpHandler(self.file_service, self.wow_service),
            "!сообщение:": CustomMessageHandler(self.file_service, self.wow_service),
            "!релоэд": ReloadHandler(self.file_service, self.wow_service),
            "!гпрл": GprlHandler(self.wow_service),
            "!сервер": ServerCheckHandler(self.file_service, self.wow_service),
        }

    async def handle_message(self, update: Update, context: CallbackContext):
        if not update.message or not update.message.text:
            return

        message_text = update.message.text.strip()
        lower_text = message_text.lower()

        # Специальная команда
        if lower_text == "вождь, покажи сиськи":
            await update.message.reply_text("( . Y . )")
            return

        # Разделяем сообщение на слова и берем первую часть (команду)
        command = message_text.split()[0].lower()

        # Ищем точное соответствие команде
        for cmd, handler in self.handlers.items():
            if command == cmd.lower():
                try:
                    await handler.handle(update, context)
                except Exception as e:
                    logger.error(f"Ошибка в обработчике {cmd}: {e}")
                    await update.message.reply_text("⚠️ Ошибка выполнения команды")
                return

        logger.debug(f"Необработанное сообщение: {message_text}")

    def run(self):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
            handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)

        application = Application.builder().token(self.config.BOT_TOKEN).build()
        application.add_handler(
            ExtMessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Основной бот запущен (без whitelist)")
        application.run_polling()
