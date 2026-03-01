# services/wow_service.py
import subprocess
import logging
import time

logger = logging.getLogger(__name__)

class WowService:
    def __init__(self, wow_commands: dict):
        self.commands = wow_commands

    def _get_wow_window_id(self) -> str:
        """Получает ID первого окна WoW"""
        try:
            result = subprocess.run(
                "wmctrl -l | grep -i 'world of warcraft' | head -1 | awk '{print $1}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=3,
            )
            window_id = result.stdout.strip()
            if not window_id:
                logger.error("Окно WoW не найдено")
                return None
            logger.info(f"Найдено окно WoW: {window_id}")
            return window_id
        except Exception as e:
            logger.error(f"Ошибка получения окна WoW: {e}")
            return None

    def _focus_wow_window(self) -> bool:
        """Активирует окно WoW"""
        window_id = self._get_wow_window_id()
        if not window_id:
            return False
        
        try:
            cmd = f"wmctrl -i -R {window_id}"
            logger.info(f"Активация окна: {cmd}")
            subprocess.run(cmd, shell=True, check=True, timeout=3)
            time.sleep(0.1)
            logger.info("Окно WoW активировано")
            return True
        except Exception as e:
            logger.error(f"Ошибка активации окна: {e}")
            return False

    def _open_chat(self) -> bool:
        """Открывает чат (Enter #1)"""
        try:
            logger.info("Enter #1 (открыть чат)...")
            subprocess.run("xte 'key Return'", shell=True, check=True, timeout=3)
            time.sleep(0.1)
            logger.info("Чат открыт")
            return True
        except Exception as e:
            logger.error(f"Ошибка открытия чата: {e}")
            return False

    def _copy_to_clipboard(self, text: str) -> bool:
        """Копирует текст в буфер"""
        try:
            cmd = f'echo -n "{text}" | xclip -selection clipboard'
            logger.info(f"Копирование в буфер: {text}")
            subprocess.run(cmd, shell=True, check=True, timeout=3)
            time.sleep(0.1)
            logger.info("Текст в буфере")
            return True
        except Exception as e:
            logger.error(f"Ошибка копирования: {e}")
            return False

    def _paste_from_clipboard(self) -> bool:
        """Вставляет из буфера (Ctrl+V)"""
        try:
            logger.info("Вставка (Ctrl+V)...")
            subprocess.run("xdotool key ctrl+v", shell=True, check=True, timeout=3)
            time.sleep(0.1)
            logger.info("Текст вставлен")
            return True
        except Exception as e:
            logger.error(f"Ошибка вставки: {e}")
            return False

    def _press_enter(self) -> bool:
        """Нажимает Enter (выполнить команду)"""
        try:
            logger.info("Enter #2 (выполнить)...")
            subprocess.run("xte 'key Return'", shell=True, check=True, timeout=3)
            time.sleep(0.1)
            logger.info("Команда отправлена")
            return True
        except Exception as e:
            logger.error(f"Ошибка Enter: {e}")
            return False

    def execute_gp_command(self) -> bool:
        """Выполняет gpEnTg() в игре"""
        try:
            logger.info("=== Начало gpEnTg() ===")
            
            if not self._focus_wow_window():
                return False
            
            if not self._open_chat():
                return False
            
            if not self._copy_to_clipboard("/run gpEnTg()"):
                return False
            
            if not self._paste_from_clipboard():
                return False
            
            if not self._press_enter():
                return False
            
            logger.info("✅ gpEnTg() выполнена успешно")
            return True
        except Exception as e:
            logger.error(f"GP command error: {e}", exc_info=True)
            return False

    def send_to_wow(self, message: str) -> bool:
        """Отправляет сообщение в WoW"""
        try:
            logger.info("=== Отправка сообщения ===")
            
            if not self._focus_wow_window():
                return False
            
            if not self._open_chat():
                return False
            
            if not self._copy_to_clipboard(message):
                return False
            
            if not self._paste_from_clipboard():
                return False
            
            if not self._press_enter():
                return False
            
            logger.info("✅ Сообщение отправлено")
            return True
        except Exception as e:
            logger.error(f"Send to WoW error: {e}", exc_info=True)
            return False

    def reload_addons(self) -> bool:
        """Выполняет /reload в игре"""
        try:
            logger.info("=== Перезагрузка аддонов ===")
            
            if not self._focus_wow_window():
                return False
            
            if not self._open_chat():
                return False
            
            if not self._copy_to_clipboard("/reload"):
                return False
            
            if not self._paste_from_clipboard():
                return False
            
            if not self._press_enter():
                return False
            
            logger.info("✅ Аддоны перезагружены")
            return True
        except Exception as e:
            logger.error(f"Reload error: {e}", exc_info=True)
            return False