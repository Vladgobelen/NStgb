# handlers/online_handler.py
from handlers.base import BaseHandler
from telegram import Update
from telegram.ext import CallbackContext
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class OnlineHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        """Команда -онлайн: сначала отвечает, потом удаляет команду"""
        try:
            url = "https://wowcircle.net/stat.html"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            output_lines = ["🎮 **Онлайн серверов WoW Circle**\n"]

            server_blocks = soup.find_all("div", class_="server-block")
            for block in server_blocks:
                title_elem = block.find("div", class_="title")
                if not title_elem:
                    continue

                title_raw = title_elem.get_text(strip=True).replace("Статус миров", "").strip()
                if "Межсерверной арены" in title_raw:
                    output_lines.append("🔹 **Межсерверные зоны**")
                else:
                    output_lines.append(f"🔹 **{title_raw}**")

                server_items = block.find_all("div", class_="server-item")
                for item in server_items:
                    name_elem = item.find("div", class_="name")
                    online_elem = item.find("div", class_="online")
                    status_div = item.find("div", class_=["on", "off"])

                    if not name_elem or not online_elem:
                        continue

                    name = name_elem.get_text(strip=True)
                    online_raw = online_elem.get_text(strip=True)
                    online = online_raw.replace("Онлайн:", "").strip()
                    status = "🟢" if status_div and "on" in status_div.get("class", []) else "🔴"

                    output_lines.append(f"{status} {name}: {online} игроков")

                output_lines.append("")  # пустая строка между блоками

            full_message = "\n".join(output_lines).rstrip()

            if len(full_message) > 4096:
                full_message = full_message[:4093] + "..."

            # 1. Сначала отправляем ответ
            sent_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=full_message,
                parse_mode="Markdown"
            )

            # 2. Потом удаляем команду (если есть разрешение)
            if update.message:
                try:
                    await update.message.delete()
                except Exception as e:
                    # Игнорируем ошибки удаления (например, в приватных чатах без прав)
                    logger.debug(f"Не удалось удалить команду: {e}")

        except Exception as e:
            logger.error(f"Ошибка в OnlineHandler: {e}", exc_info=True)
            fallback_msg = await update.message.reply_text("⚠️ Не удалось загрузить или распарсить данные онлайн")
            try:
                await update.message.delete()
            except:
                pass