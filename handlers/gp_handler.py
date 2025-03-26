from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000  # Лимит Telegram на сообщение


class GpHandler(BaseHandler):
    async def _send_chunks(self, update: Update, text: str, prefix: str = ""):
        """Отправляет длинный текст частями"""
        while text:
            chunk = text[:MAX_MESSAGE_LENGTH]
            text = text[MAX_MESSAGE_LENGTH:]

            # Находим последний перенос строки в чанке
            last_newline = chunk.rfind("\n")
            if last_newline != -1 and len(text) > 0:
                chunk = chunk[:last_newline]
                text = chunk[last_newline + 1 :] + text

            await update.message.reply_text(prefix + chunk)
            prefix = ""  # Префикс только для первого сообщения

    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!гп'"""
        if not await self.check_access(update):
            return

        try:
            # Получаем аргументы после команды
            args = update.message.text.strip().split()[1:]

            # Загрузка данных GP
            data = self.file_service.load_gp_data()
            if not data:
                await update.message.reply_text("Данные GP не найдены")
                return

            gp_data = dict(sorted(data.items(), key=lambda item: item[1]))
            result = []

            # Обработка разных вариантов запроса
            if len(args) == 0:  # Все записи
                for name, value in gp_data.items():
                    result.append(f"{name}: {int(value)}")

            elif len(args) == 1:  # По имени
                name = args[0]
                if name in gp_data:
                    result.append(f"{name}: {int(gp_data[name])}")
                else:
                    await update.message.reply_text("Игрок не найден")
                    return

            elif len(args) == 2:  # По диапазону
                try:
                    min_val, max_val = int(args[0]), int(args[1])
                    for name, value in gp_data.items():
                        if min_val <= int(value) <= max_val:
                            result.append(f"{name}: {int(value)}")
                except ValueError:
                    await update.message.reply_text("Неверный формат чисел")
                    return

            else:
                await update.message.reply_text(
                    "Использование: !гп [имя] или !гп [мин] [макс]"
                )
                return

            # Отправка результата
            if not result:
                await update.message.reply_text("Нет данных по вашему запросу")
            else:
                full_text = "📊 GP статистика:\n" + "\n".join(result)
                await self._send_chunks(update, full_text)

        except Exception as e:
            logger.error(f"Error in GpHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при обработке запроса GP")
