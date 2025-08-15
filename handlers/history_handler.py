# handlers/history_handler.py
from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MAX_LINES = 10  # Максимум строк за раз, чтобы не засорять чат


class HistoryHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        try:
            message_text = update.message.text.strip()

            # Проверяем, что команда начинается с `-история`
            if not message_text.lower().startswith("-история"):
                return

            # Извлекаем аргументы
            args = message_text[9:].strip().split()
            if not args:
                args = []

            # Загружаем историю
            raw_lines = self.file_service.load_chat_history()
            if not raw_lines:
                await update.message.reply_text("История чата пуста или не загружена")
                return

            # Парсим каждую строку: "Ник Сообщение timestamp"
            parsed = []
            for line in raw_lines:
                line = line.strip()
                if not line:
                    continue

                # Ищем последнее число (timestamp)
                match = re.match(r'^(.+?)\s+(\d{10,})$', line)
                if match:
                    text_part = match.group(1).strip()
                    timestamp = int(match.group(2))

                    # Первое слово — ник
                    first_space = text_part.find(' ')
                    if first_space > 0:
                        nick = text_part[:first_space]
                        message = text_part[first_space + 1:].strip()
                    else:
                        nick = "Unknown"
                        message = text_part
                else:
                    nick = "Unknown"
                    message = line
                    timestamp = 0

                time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S") if timestamp >= 1000000000 else "??:??:??"

                parsed.append({
                    "nick": nick,
                    "message": message,
                    "timestamp": timestamp,
                    "time_str": time_str
                })

            # Определяем: ник, диапазон
            target_nick = None
            start_idx = None
            end_idx = None

            # Проверяем первый аргумент: если не число — это ник
            if args:
                if not args[0].isdigit():
                    target_nick = args[0]
                    args = args[1:]

            # Диапазон
            if len(args) >= 2:
                try:
                    start_idx = int(args[0]) - 1
                    end_idx = int(args[1])
                    if start_idx < 0:
                        start_idx = 0
                except ValueError:
                    await update.message.reply_text("❌ Диапазон должен быть числом")
                    return
            elif len(args) == 1 and args[0].isdigit():
                try:
                    end_idx = int(args[0])
                    start_idx = 0
                except ValueError:
                    pass

            # Фильтр по нику
            if target_nick:
                filtered = [p for p in parsed if p["nick"] == target_nick]
                total_count = len(filtered)
                if total_count == 0:
                    await update.message.reply_text(f"🔸 Ник '{target_nick}' не найден в истории")
                    return
            else:
                filtered = parsed
                total_count = len(filtered)

            # Выбор диапазона
            if start_idx is None and end_idx is None:
                selected = filtered[-10:]
            elif start_idx is not None and end_idx is not None:
                selected = filtered[start_idx:end_idx]
            elif end_idx is not None:
                selected = filtered[:end_idx]
            else:
                selected = filtered[-10:]  # fallback

            # Ограничение
            if len(selected) > MAX_LINES:
                await update.message.reply_text(f"⚠️ Слишком много строк ({len(selected)}). Максимум: {MAX_LINES}")
                selected = selected[:MAX_LINES]

            if not selected:
                await update.message.reply_text("🔸 Нет сообщений по заданному фильтру")
                return

            # Формируем ответ
            result_lines = []
            for item in selected:
                result_lines.append(f"[{item['time_str']}] {item['nick']}: {item['message']}")

            header = "📜 История чата:"
            if target_nick:
                header += f" @{target_nick}"
            if start_idx is not None or end_idx is not None:
                range_str = f"{start_idx + 1}–{end_idx if end_idx else len(filtered)}"
                header += f" [{range_str}]"

            await update.message.reply_text(header + "\n" + "\n".join(result_lines))

        except Exception as e:
            logger.error(f"Ошибка в HistoryHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при обработке истории")