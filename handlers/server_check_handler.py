from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import subprocess
import logging

logger = logging.getLogger(__name__)


class ServerCheckHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Обработчик команды '!проверка_сервера'"""
        if not await self.check_access(update):
            return

        try:
            await update.message.reply_text("🔄 Проверяю состояние сервера...")

            # Проверка наличия соединений
            result_count = subprocess.run(
                'netstat | grep "11294" | wc -l',
                shell=True,
                capture_output=True,
                text=True,
            )
            connection_count = int(result_count.stdout.strip() or 0)

            if connection_count < 1:
                await update.message.reply_text("🔴 Сервер ОФФЛАЙН")
                return

            # Проверка проблем при наличии соединений
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
                await update.message.reply_text(
                    f"🟡 Сервер БОЛЕЕТ ({', '.join(problems)})"
                )
            else:
                await update.message.reply_text("🟢 Сервер ОНЛАЙН")

        except Exception as e:
            logger.error(f"Ошибка проверки сервера: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при проверке сервера")
