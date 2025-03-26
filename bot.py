import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler as ExtMessageHandler,
    CallbackContext,
    filters,
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
        self.whitelist = self.file_service.load_whitelist(self.config.WHITELIST_FILE)

        self.handlers = {
            "илвл": IlvlHandler(self.file_service, self.wow_service, self.whitelist),
            "!гп": GpHandler(self.file_service, self.wow_service, self.whitelist),
            "!сообщение:": CustomMessageHandler(
                self.file_service, self.wow_service, self.whitelist
            ),
            "!релоэд": ReloadHandler(
                self.file_service, self.wow_service, self.whitelist
            ),
            "!гпрл": GprlHandler(self.wow_service, self.whitelist),
            "!проверка_сервера": ServerCheckHandler(
                self.file_service, self.wow_service, self.whitelist
            ),
        }

    async def post_init(self, application: Application):
        application.bot_data["state"] = self

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        if self.is_user_confirmed(user.id):
            await self.show_commands(update, context)
        else:
            await update.message.reply_text(
                "👋 Привет! Для доступа к функциям бота:\n"
                "1. Присоединитесь к нашей группе\n"
                "2. Отправьте команду /confirm"
            )

    async def show_commands(self, update: Update, context: CallbackContext):
        buttons = [
            ["📊 GP статистика", "🔄 Обновление данных"],
            ["📨 Сообщение в чат", "📡 Проверить сервер"],
            ["📈 Уровень предметов"],
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        await update.message.reply_text("Выберите команду:", reply_markup=reply_markup)

    async def handle_message(self, update: Update, context: CallbackContext):
        user = update.effective_user
        if not self.is_user_confirmed(user.id):
            await self._handle_unauthorized(update, context)
            return

        text = update.message.text.lower()

        # Обработка кнопок
        if text == "📊 gp статистика":
            await self.handlers["!гп"].handle(update, context)
        elif text == "🔄 релоад":
            await self.handlers["!релоэд"].handle(update, context)
        elif text == "📨 сообщение в чат":
            await update.message.reply_text(
                "Введите сообщение в формате: !сообщение: ваш текст",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
        elif text == "📡 проверить сервер":
            await self.handlers["!проверка_сервера"].handle(update, context)
        elif text == "📈 уровень предметов":
            await self.handlers["илвл"].handle(update, context)
        elif text == "назад":
            await self.show_commands(update, context)
        else:
            # Обработка текстовых команд
            await self._handle_text_commands(update, context)

    async def _handle_text_commands(self, update: Update, context: CallbackContext):
        text = update.message.text.lower()
        parts = text.split()
        if not parts:
            return

        command = parts[0]
        for cmd, handler in self.handlers.items():
            if command == cmd.lower():
                await handler.handle(update, context)
                return

    async def _handle_unauthorized(self, update: Update, context: CallbackContext):
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение: {e}")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{update.effective_user.first_name}, для доступа к боту выполните /confirm",
            reply_markup=ReplyKeyboardRemove(),
        )

    def is_user_confirmed(self, user_id: int) -> bool:
        return user_id in self.whitelist

    def run(self):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
            handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
        )
        logging.getLogger("httpx").setLevel(logging.WARNING)

        application = (
            Application.builder()
            .token(self.config.BOT_TOKEN)
            .post_init(self.post_init)
            .build()
        )

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("confirm", self.confirm))
        application.add_handler(CommandHandler("commands", self.show_commands))
        application.add_handler(
            ExtMessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Бот запущен с кнопочным управлением")
        application.run_polling()
