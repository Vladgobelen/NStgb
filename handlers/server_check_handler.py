from handlers.base import BaseHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
import subprocess
import logging

logger = logging.getLogger(__name__)


class ServerCheckHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды проверки сервера"""
        if not await self.check_access(update):
            return

        # Проверяем, что это команда проверки (кнопка или текст)
        text = update.message.text
        if not (text.lower() == "!проверка_сервера" or text == "📡 Проверить сервер"):
            return

        try:
            await update.message.reply_text(
                "🔄 Проверяю состояние сервера...",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )

            # Проверка соединений
            result_count = subprocess.run(
                'netstat | grep "11294" | wc -l',
                shell=True,
                capture_output=True,
                text=True,
            )
            connection_count = int(result_count.stdout.strip() or 0)

            if connection_count < 1:
                await update.message.reply_text(
                    "🔴 Сервер ОФФЛАЙН",
                    reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
                )
                return

            # Дополнительные проверки
            result_conn = subprocess.run(
                "netstat | grep ':11294 ' | awk '{print $3}'",
                shell=True,
                capture_output=True,
                text=True,
            )
            connections = [int(x) for x in result_conn.stdout.split() if x.isdigit()]

            result_packets = subprocess.run(
                "netstat | grep ':11294 ' | awk '{print $2}'",
                shell=True,
                capture_output=True,
                text=True,
            )
            packets = [int(x) for x in result_packets.stdout.split() if x.isdigit()]

            problems = []
            if any(c > 500 for c in connections):
                problems.append("соединения")
            if any(p > 50000 for p in packets):
                problems.append("пакеты")

            if problems:
                response = f"🟡 Сервер БОЛЕЕТ ({', '.join(problems)})"
            else:
                response = "🟢 Сервер ОНЛАЙН"

            await update.message.reply_text(
                response,
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )

        except Exception as e:
            logger.error(f"Ошибка проверки сервера: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Ошибка при проверке сервера",
                reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True),
            )
