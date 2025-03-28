import logging
from telegram import Update
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
import asyncio

logger = logging.getLogger(__name__)


class WowBot:
    def __init__(self):
        # Инициализация конфигурации
        self.config = Config()

        # Инициализация сервисов
        self.file_service = FileService(self.config.WOW_FILES)
        self.wow_service = WowService(self.config.WOW_COMMANDS)

        # Загрузка белого списка
        self.whitelist = self.file_service.load_whitelist(self.config.WHITELIST_FILE)
        logger.info(f"Загружен белый список: {len(self.whitelist)} пользователей")

        # Инициализация обработчиков команд
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
            "!сервер": ServerCheckHandler(
                self.file_service, self.wow_service, self.whitelist
            ),
        }

    def is_user_confirmed(self, user_id: int) -> bool:
        """Проверяет, есть ли пользователь в белом списке"""
        return user_id in self.whitelist

    async def post_init(self, application: Application):
        """Инициализация после запуска"""
        application.bot_data["state"] = self

    async def _delete_message_with_retry(
        self, chat_id: int, message_id: int, context: CallbackContext = None
    ):
        """Удаление сообщения с повторными попытками"""
        max_attempts = 5
        initial_delay = 1
        attempt = 0

        while attempt < max_attempts:
            try:
                if context:
                    await context.bot.delete_message(
                        chat_id=chat_id, message_id=message_id
                    )
                else:
                    # Если context не передан, создаем временный Application
                    async with Application.builder().token(
                        self.config.BOT_TOKEN
                    ).build() as app:
                        await app.bot.delete_message(
                            chat_id=chat_id, message_id=message_id
                        )

                logger.info(f"Сообщение {message_id} успешно удалено")
                return True
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    logger.error(
                        f"Не удалось удалить сообщение после {max_attempts} попыток: {e}"
                    )
                    return False

                delay = initial_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"Попытка {attempt} не удалась, повтор через {delay} сек: {e}"
                )
                await asyncio.sleep(delay)

    async def _schedule_message_deletion(
        self, context: CallbackContext, chat_id: int, message_id: int, delay: int = 30
    ):
        """Планирует удаление сообщения через указанное время"""
        try:
            context.job_queue.run_once(
                callback=lambda ctx: self._delete_message_with_retry(
                    chat_id, message_id, ctx
                ),
                when=delay,
                data={"chat_id": chat_id, "message_id": message_id},
                name=f"delete_msg_{message_id}",
            )
        except Exception as e:
            logger.error(f"Ошибка при планировании удаления сообщения: {e}")

    async def start(self, update: Update, context: CallbackContext):
        """Обработчик команды /start"""
        user = update.effective_user
        if self.is_user_confirmed(user.id):
            msg = await update.message.reply_text("✅ Вы уже подтверждены!")
        else:
            msg = await update.message.reply_text(
                "👋 Привет! Для доступа к функциям бота:\n"
                "1. Присоединитесь к нашей группе\n"
                "2. Отправьте команду /confirm"
            )
        await self._schedule_message_deletion(
            context, update.effective_chat.id, msg.message_id
        )

    async def confirm(self, update: Update, context: CallbackContext):
        """Обработчик команды /confirm"""
        user = update.effective_user
        try:
            # Удаление сообщения с /confirm
            try:
                await update.message.delete()
            except Exception as e:
                logger.error(f"Не удалось удалить сообщение: {e}")

            if self.is_user_confirmed(user.id):
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="ℹ️ Вы уже подтверждены.",
                )
                await self._schedule_message_deletion(
                    context, update.effective_chat.id, msg.message_id
                )
                return

            # Проверка членства в группе
            chat_member = await context.bot.get_chat_member(
                self.config.GROUP_CHAT_ID, user.id
            )

            if chat_member.status in ["administrator", "creator", "member"]:
                if self.file_service.save_to_whitelist(
                    self.config.WHITELIST_FILE,
                    user.id,
                    user.username or user.first_name,
                ):
                    self.whitelist.add(user.id)
                    text = (
                        "✅ Вы успешно подтверждены!"
                        if chat_member.status == "member"
                        else "👑 Администратор подтвержден!"
                    )
                    msg = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=text,
                    )
                    await self._schedule_message_deletion(
                        context, update.effective_chat.id, msg.message_id
                    )
                    return

            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Вы должны быть участником группы!",
            )
            await self._schedule_message_deletion(
                context, update.effective_chat.id, msg.message_id
            )

        except Exception as e:
            logger.error(f"Ошибка подтверждения: {e}", exc_info=True)
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла ошибка. Попробуйте позже.",
            )
            await self._schedule_message_deletion(
                context, update.effective_chat.id, msg.message_id
            )

    async def _delete_warning_message(self, context: CallbackContext):
        """Удаляет предупреждающее сообщение"""
        await self._delete_message_with_retry(
            context.job.data["chat_id"], context.job.data["message_id"], context
        )

    async def handle_message(self, update: Update, context: CallbackContext):
        """Обработка входящих сообщений"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_text = update.message.text.strip()

        # 1. Проверка доступа пользователя
        if not self.is_user_confirmed(user.id):
            try:
                await update.message.delete()
                logger.info(
                    f"Удалили сообщение от неподтвержденного пользователя {user.id}"
                )
            except Exception as e:
                logger.error(f"Ошибка удаления сообщения: {e}")

            # Отправляем сообщение с таймером удаления
            warning_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=f"{user.first_name}, для доступа к чату выполните /confirm",
            )

            # Пытаемся запланировать удаление
            try:
                context.job_queue.run_once(
                    callback=self._delete_warning_message,
                    when=30,
                    data={
                        "chat_id": chat_id,
                        "message_id": warning_msg.message_id,
                        "user_id": user.id,
                    },
                    name=f"delete_warning_{user.id}_{warning_msg.message_id}",
                )
            except Exception as e:
                logger.error(f"Ошибка при планировании удаления: {e}")
            return

        text = message_text.lower()

        # Специальные случаи (не команды)
        if text == "вождь, покажи сиськи":
            msg = await update.message.reply_text("( . Y . )")
            await self._schedule_message_deletion(context, chat_id, msg.message_id)
            return

        # Разделяем сообщение на слова
        parts = text.split()
        if not parts:
            return

        # Получаем первую часть команды (первое слово)
        command = parts[0]

        # Ищем точное соответствие команды
        for cmd, handler in self.handlers.items():
            if command == cmd.lower():
                await handler.handle(update, context)
                return

        # Если команда не найдена
        logger.info(
            f"Подтвержденный пользователь {user.id} отправил некомандное сообщение: {text}"
        )

    def run(self):
        """Запуск бота"""
        # Настройка логирования
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

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("confirm", self.confirm))
        application.add_handler(
            ExtMessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Бот запущен")
        application.run_polling()
