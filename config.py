import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", -1001380105834))
        self.WHITELIST_FILE = Path(os.getenv("WHITELIST_FILE", "whitelist.txt"))

        self.WOW_FILES = {
            "ilvl": Path(
                "/home/diver/Games/wc/CircleL/WTF/Account/VLADGOBELEN/SavedVariables/NSQC.lua"
            ),
            "gp": Path(
                "/home/diver/Games/wc/CircleL/WTF/Account/VLADGOBELEN/SavedVariables/NSQC.lua"
            ),
            "history": Path(
                "/home/diver/Games/wc/CircleL/WTF/Account/VLADGOBELEN/SavedVariables/GuildChat.lua"
            ),
        }

        self.WOW_COMMANDS = {
            "focus_window": [
                "env DISPLAY=:0 lua /home/diver/Скрипты/lo.lua",
                "env DISPLAY=:0 sh /home/diver/Скрипты/l211.sh",
                "xte 'key Return'",  # Активация чата
            ],
            "paste_command": "xte 'keydown Control_L' 'key v' 'keyup Control_L'",
            "press_enter": "xte 'key Return'",
        }

        # Все команды в нижнем регистре для единообразия
        self.COMMAND_PREFIXES = {
            "илвл": "ilvl",
            "!гп": "gp",
            "!сообщение:": "message",
            "!релоэд": "reload",
            "!гпрл": "gprl",
        }

    def _get_env_var(self, var_name: str, default=None):
        value = os.getenv(var_name, default)
        if value is None:
            raise ValueError(f"Не задана обязательная переменная окружения: {var_name}")
        return value
