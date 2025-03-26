import subprocess
import shlex
import pyperclip
import logging

logger = logging.getLogger(__name__)


class WowService:
    def __init__(self, wow_commands: dict):
        self.commands = wow_commands

    def _run_cmd(self, command: str) -> bool:
        """Выполнение одной команды"""
        try:
            subprocess.run(shlex.split(command), check=True, timeout=3)
            return True
        except Exception as e:
            logger.error(f"Command failed: {command} - {e}")
            return False

    def execute_gp_command(self) -> bool:
        """ТОЛЬКО выполняет команду в игре, без доступа к файлам"""
        try:
            # 1. Активация окна
            for cmd in self.commands["focus_window"]:
                if not self._run_cmd(cmd):
                    return False

            # 2. Отправка команды
            pyperclip.copy("/run gpEnTg()")
            return self._run_cmd(self.commands["paste_command"]) and self._run_cmd(
                self.commands["press_enter"]
            )

        except Exception as e:
            logger.error(f"GP command error: {e}")
            return False

    def send_to_wow(self, message: str) -> bool:
        """Отправка сообщения в игру (аналог handle_custom_message из старого бота)"""
        try:
            pyperclip.copy(message)
            for cmd in self.commands["focus_window"]:
                if not self._run_cmd(cmd):
                    return False
            return self._run_cmd(self.commands["paste_command"]) and self._run_cmd(
                self.commands["press_enter"]
            )
        except Exception as e:
            logger.error(f"Send to WoW error: {e}")
            return False

    def reload_addons(self) -> bool:
        """Релоад аддонов (аналог handle_reload из старого бота)"""
        try:
            for cmd in self.commands["focus_window"]:
                if not self._run_cmd(cmd):
                    return False

            pyperclip.copy("/reload")
            return self._run_cmd(self.commands["paste_command"]) and self._run_cmd(
                self.commands["press_enter"]
            )
        except Exception as e:
            logger.error(f"Reload error: {e}")
            return False
