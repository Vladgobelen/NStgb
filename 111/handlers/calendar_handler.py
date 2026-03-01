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

    def _format_events(self, day_dict, target_nick: str = None) -> list:
        """Форматирует события в читаемый список"""
        events = []
        for sender, sender_events in day_dict.items():
            if target_nick and sender != target_nick:
                continue
            for title, event in sender_events.items():
                time_str = event.get("date", "0000")
                formatted_time = f"{time_str[:2]}:{time_str[2:]}" if len(time_str) == 4 else time_str
                desc_raw = event.get("text", "")
                logger.debug(f"[DEBUG CALENDAR] desc_raw = {repr(desc_raw)}")
                print(f"[PRINT DEBUG] RAW DESCRIPTION: {repr(desc_raw)}")

                # Заменяем литеральные управляющие последовательности на реальные символы
                desc = desc_raw.replace('\\n', '\n').replace('\\r', '\r')
                # Убираем пробельные символы и остаточные обратные слеши в конце
                desc = desc.rstrip(' \t\r\n\\')

                logger.debug(f"[DEBUG CALENDAR] desc after cleanup = {repr(desc)}")
                print(f"[PRINT DEBUG] CLEANED DESCRIPTION: {repr(desc)}")

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
            mode = "today"

            if not args:
                target_date = now.strftime("%Y-%m-%d")
                mode = "today"
            else:
                arg = args[0]
                if arg.isdigit() and 1 <= int(arg) <= 31:
                    day = int(arg)
                    try:
                        target_date = now.replace(day=day).strftime("%Y-%m-%d")
                    except ValueError:
                        await update.message.reply_text("❌ Некорректная дата")
                        return
                    mode = "date"
                elif '.' in arg:
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
                    target_nick = arg
                    target_date = now.strftime("%Y-%m-%d")
                    mode = "nick"

            events = []
            fallback_used = False

            if target_date in calendar:
                events = self._format_events(calendar[target_date], target_nick)
            else:
                if mode in ("today", "nick"):
                    last_date = self._find_last_available_date(calendar)
                    if last_date and last_date in calendar:
                        events = self._format_events(calendar[last_date], target_nick)
                        target_date = last_date
                        fallback_used = True

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

                full_output = header + "\n\n" + "\n\n".join(events)
                logger.debug(f"[DEBUG CALENDAR] Final output:\n{repr(full_output)}")
                await update.message.reply_text(full_output)

        except Exception as e:
            logger.error(f"Ошибка в CalendarHandler: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Ошибка при обработке календаря")
