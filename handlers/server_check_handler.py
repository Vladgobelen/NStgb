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

            # Проверка 1: Количество соединений
            result = subprocess.run(
                "netstat | grep ':11294 ' | awk '{print $3}'",
                shell=True,
                capture_output=True,
                text=True,
            )
            connections = [int(x) for x in result.stdout.split() if x.isdigit()]

            # Проверка 2: Количество пакетов
            result_packets = subprocess.run(
                "netstat | grep ':11294 ' | awk '{print $2}'",
                shell=True,
                capture_output=True,
                text=True,
            )
            packets = [int(x) for x in result_packets.stdout.split() if x.isdigit()]

            # Проверка 3: Наличие соединений
            result_count = subprocess.run(
                'netstat | grep "11294" | wc -l',
                shell=True,
                capture_output=True,
                text=True,
            )
            connection_count = int(result_count.stdout.strip() or 0)

            # Формируем отчет
            report = "📊 Статус сервера:\n"
            report += f"• Активных соединений: {connection_count}\n"

            if connections:
                report += f"• Макс. соединений: {max(connections)}\n"
            else:
                report += "• Нет данных о соединениях\n"

            if packets:
                report += f"• Макс. пакетов: {max(packets)}\n"
            else:
                report += "• Нет данных о пакетах\n"

            # Проверка на проблемы
            problems = []
            if connection_count < 1:
                problems.append("⚠️ Нет активных соединений")
            if any(c > 500 for c in connections):
                problems.append("⚠️ Превышено количество соединений (>500)")
            if any(p > 50000 for p in packets):
                problems.append("⚠️ Превышено количество пакетов (>50000)")

            if problems:
                report += "\n🚨 Проблемы:\n" + "\n".join(problems)
            else:
                report += "\n✅ Все системы работают нормально"

            await update.message.reply_text(report)

        except Exception as e:
            logger.error(f"Ошибка проверки сервера: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при проверке сервера")
