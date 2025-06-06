import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")

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
                "xte 'key Return'",
            ],
            "paste_command": "xte 'keydown Control_L' 'key v' 'keyup Control_L'",
            "press_enter": "xte 'key Return'",
        }
