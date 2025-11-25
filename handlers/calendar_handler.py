# handlers/calendar_handler.py
from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CalendarHandler(BaseHandler):
    def _find_last_available_date(self, calendar: dict) -> str:
        """Находит самую свежую дату в календаре"""
        dates = list(calendar.keys())
        if not dates:
            return None
        return max(dates)

    def _format_events(self, day_data: dict, target_nick: str = None) -> list:
        """Форматирует события в читаемый список"""
        events = []
        for sender, sender_events in day_data.items():
            if target_nick and sender != target_nick:
                continue
            for title, event in sender_events.items():
                time_str = event.get("date", "0000")
                formatted_time = f"{time_str[:2]}:{time_str[2:]}" if len(time_str) == 4 else time_str
                desc = event.get("text", "")
                event_line = f"📌 {title} ({formatted_time})\n👤 {sender}"
                if desc:
                    event_line += f"\n📝 {desc}"
                events.append(event_line)
        return events

    async def handle(self, update: Update, context: CallbackContext):
        try:
            message_text = update.message.text.strip()
            if not message_text.lower().startswith("-рт"):
                return

            args = message_text[4:].strip().split()  # убираем "-рт"

            full_data = self.file_service.load_lua_file("calendar")
            if not full_data or "calendar" not in full_data:
                await update.message.reply_text("📅 Календарь пуст или не загружен")
                return

            calendar = full_data["calendar"]
            now = datetime.now()
            target_date = None
            target_nick = None
            mode = "today"  # today, date, nick

            if not args:
                # Режим: сегодня
                target_date = now.strftime("%Y-%m-%d")
                mode = "today"
            else:
                arg = args[0]
                if arg.isdigit() and 1 <= int(arg) <= 31:
                    # Режим: дата (DD)
                    day = int(arg)
                    try:
                        target_date = now.replace(day=day).strftime("%Y-%m-%d")
                    except ValueError:
                        await update.message.reply_text("❌ Некорректная дата")
                        return
                    mode = "date"
                elif '.' in arg:
                    # Режим: дата (DD.MM)
                    parts = arg.split('.', 1)
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        day, month = int(parts[0]), int(parts[1])
                        try:
                            target_date = now.replace(day=day, month=month).strftime("%Y-%m-%d")
                        except ValueError:
                            await update.message.reply_text("❌ Некорректная дата (DD.MM)")
                            return
                    else:
                        await update.message.reply_text("❌ Формат даты: DD или DD.MM")
                        return
                    mode = "date"
                else:
                    # Режим: ник
                    target_nick = arg
                    target_date = now.strftime("%Y-%m-%d")
                    mode = "nick"

            events = []
            fallback_used = False

            # Пытаемся найти события на целевой дате
            if target_date in calendar:
                events = self._format_events(calendar[target_date], target_nick)
            else:
                # Если дата не указана явно (today/nick) — ищем последнюю доступную
                if mode in ("today", "nick"):
                    last_date = self._find_last_available_date(calendar)
                    if last_date and last_date in calendar:
                        events = self._format_events(calendar[last_date], target_nick)
                        target_date = last_date
                        fallback_used = True
                # Если указана дата (mode == "date") — не делаем fallback

            # Формируем ответ
            if not events:
                if mode == "date":
                    date_display = datetime.fromisoformat(target_date).strftime("%d.%m.%Y")
                    await update.message.reply_text(f"📅 Нет событий на {date_display}")
                else:
                    msg = "📅 Сегодня нет событий"
                    if fallback_used:
                        date_display = datetime.fromisoformat(target_date).strftime("%d.%m.%Y")
                        msg += f", но есть на {date_display}"
                    await update.message.reply_text(msg)
            else:
                date_display = datetime.fromisoformat(target_date).strftime("%d.%m.%Y")
                if fallback_used and mode == "today":
                    header = f"📅 Сегодня нет событий. Последние события на {date_display}:"
                elif fallback_used and mode == "nick":
                    header = f"📅 Сегодня нет событий от **{target_nick}**. Последние на {date_display}:"
                else:
                    header = f"📅 События на {date_display}"
                    if target_nick:
                        header += f" (от {target_nick})"

                await update.message.reply_text(header + "\n\n" + "\n\n".join(events))

        except Exception as e:
            logger.error(f"Ошибка в CalendarHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при обработке календаря")