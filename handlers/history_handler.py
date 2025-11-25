# handlers/history_handler.py
from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MAX_LINES = 10  # Максимум строк при выводе сообщений
TOTAL_BASE = 10000  # База для расчёта процента
TOP_COUNT = 10  # Сколько игроков в топе


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

            # Парсим каждую строку: ищем timestamp в конце
            parsed = []
            for line in raw_lines:
                line = line.strip()
                if not line:
                    continue

                # Ищем timestamp из 10+ цифр в конце строки
                timestamp_match = re.search(r'(\d{10,})$', line)
                if timestamp_match:
                    timestamp = int(timestamp_match.group(1))
                    text_part = line[:timestamp_match.start()].strip()
                    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                else:
                    # Нет timestamp — пропускаем или помечаем как неизвестное
                    timestamp = 0
                    text_part = line
                    time_str = "??:??:??"

                # Извлекаем ник: первое слово до пробела
                if text_part:
                    first_space = text_part.find(' ')
                    if first_space > 0:
                        nick = text_part[:first_space]
                        message = text_part[first_space + 1:].strip()
                    else:
                        nick = text_part  # только ник, без сообщения
                        message = ""
                else:
                    nick = "Unknown"
                    message = ""

                parsed.append({
                    "nick": nick,
                    "message": message,
                    "timestamp": timestamp,
                    "time_str": time_str
                })

            total_messages = len(parsed)

            # === КОМАНДА: топ ===
            if len(args) == 1 and args[0].lower() == "топ":
                # Считаем количество сообщений по никам
                stats = {}
                for p in parsed:
                    nick = p["nick"]
                    if nick != "Unknown":
                        stats[nick] = stats.get(nick, 0) + 1

                # Сортируем по убыванию
                sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

                # Формируем топ-10
                lines = ["🏆 ТОП-10 по активности в чате:"]
                for i, (nick, count) in enumerate(sorted_stats[:TOP_COUNT], 1):
                    percent = (count / total_messages) * 100 if total_messages > 0 else 0
                    lines.append(f"{i}. {nick} — {count} сообщений ({percent:.2f}%)")

                if not sorted_stats:
                    lines.append("Пока нет данных")

                await update.message.reply_text("\n".join(lines))
                return

            # === КОМАНДА: [Ник] всего ===
            if len(args) >= 2 and args[1].lower() == "всего":
                target_nick = args[0]
                count = sum(1 for p in parsed if p["nick"] == target_nick)

                if count == 0:
                    await update.message.reply_text(f"🔸 Ник \"{target_nick}\" не найден в истории")
                    return

                percent = (count / total_messages) * 100 if total_messages > 0 else 0
                await update.message.reply_text(
                    f"📊 Ник \"{target_nick}\" написал {count} сообщений "
                    f"({percent:.2f}% от {total_messages})"
                )
                return

            # === ОСНОВНАЯ ЛОГИКА: диапазон, фильтр по нику и т.д. ===

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
