from handlers.base import BaseHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)


class GpHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды ГП с поддержкой кнопок"""
        if not await self.check_access(update):
            return

        # Проверяем, что это команда ГП (кнопка или текстовая команда)
        text = update.message.text
        is_button = text == "📊 ГП статистика"
        is_command = text.lower().startswith("!гп")

        if not (is_button or is_command):
            return

        try:
            # Получаем аргументы
            args = text.split()[1:] if is_command else []

            # Загрузка данных ГП
            data = self.file_service.load_gp_data()
            if not data:
                await update.message.reply_text(
                    "Данные ГП не найдены",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
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
                    await update.message.reply_text(
                        "Игрок не найден",
                        reply_markup=ReplyKeyboardMarkup(
                            [["Назад"]], resize_keyboard=True
                        ),
                    )
                    return
            elif len(args) == 2:  # По диапазону
                try:
                    min_val, max_val = int(args[0]), int(args[1])
                    for name, value in gp_data.items():
                        if min_val <= int(value) <= max_val:
                            result.append(f"{name}: {int(value)}")
                except ValueError:
                    await update.message.reply_text(
                        "Неверный формат чисел",
                        reply_markup=ReplyKeyboardMarkup(
                            [["Назад"]], resize_keyboard=True
                        ),
                    )
                    return
            else:
                await update.message.reply_text(
                    "Использование: !гп [имя] или !гп [мин] [макс]",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
                return

            # Отправка результата
            if not result:
                response = "Нет данных по вашему запросу"
            else:
                response = "📊 ГП статистика:\n" + "\n".join(
                    result[:50]
                )  # Ограничение на 50 записей

            await update.message.reply_text(
                response,
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )

        except Exception as e:
            logger.error(f"Error in GpHandler: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Ошибка при обработке запроса ГП",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
