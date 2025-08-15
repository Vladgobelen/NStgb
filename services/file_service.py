# services/file_service.py
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from slpp import slpp as lua

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, file_paths: Dict[str, Path]):
        self.file_paths = file_paths

    def find_table(self, data: str, name: str) -> Optional[str]:
        res = re.search(r"\s%s = (.*?)\n}" % name, data, re.DOTALL)
        return res.group(1) + "\n}" if res else None

    def load_lua_file(self, file_type: str) -> Optional[Dict[str, Any]]:
        file_path = self.file_paths.get(file_type)
        if not file_path or not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            table_data = self.find_table(data, "nsDb") or self.find_table(data, "testQ")
            if not table_data:
                logger.error(f"Таблица nsDb/testQ не найдена в файле {file_path}")
                return None

            return lua.decode(table_data)
        except Exception as e:
            logger.error(f"Error loading Lua file: {e}", exc_info=True)
            return None

    def load_gp_data(self) -> Optional[dict]:
        try:
            data = self.load_lua_file("gp")
            if not data:
                return None

            if "testQ" in data and "gpEnTg" in data["testQ"]:
                return data["testQ"]["gpEnTg"]
            elif "gpEnTg" in data:
                return data["gpEnTg"]
            elif "gpDB" in data:
                return data["gpDB"]
            elif "nsDb" in data and "gpEnTg" in data["nsDb"]:
                return data["nsDb"]["gpEnTg"]

            logger.error(f"GP данные не найдены в структуре: {list(data.keys())}")
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки GP данных: {e}", exc_info=True)
            return None

    def load_whitelist(self, whitelist_path: Path) -> set[int]:
        whitelist = set()
        try:
            if whitelist_path.exists():
                with open(whitelist_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip() and line.split()[0].isdigit():
                            whitelist.add(int(line.split()[0]))
            else:
                logger.warning(f"Файл белого списка не найден: {whitelist_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки whitelist: {e}", exc_info=True)
        return whitelist

    def load_chat_history(self) -> Optional[list]:
        """
        Загружает список сообщений из ns_chat_log['лог_чат']
        Точечно извлекает массив строк, игнорируя остальной код.
        Использует ручной парсинг с балансировкой фигурных скобок.
        """
        file_path = self.file_paths.get("history")
        if not file_path or not file_path.exists():
            logger.error(f"❌ Файл истории не найден: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            logger.info(f"🔍 Начинаем парсинг истории чата из {file_path}")

            start_marker = '["лог_чат"] = {'
            start = data.find(start_marker)
            if start == -1:
                logger.error('❌ Не найден маркер ["лог_чат"] = {')
                return None

            # Начинаем после {
            start += len(start_marker)
            brace_count = 1
            i = start
            content_lines = []

            # Балансировка скобок
            while i < len(data) and brace_count > 0:
                if data[i] == '{':
                    brace_count += 1
                elif data[i] == '}':
                    brace_count -= 1
                i += 1

            # Вырезаем содержимое между { и последней }
            content = data[start:i-1]

            # Удаляем комментарии -- [число]
            content = re.sub(r'--\s*\[\d+\]', '', content)

            # Разбиваем на строки
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                # Убираем кавычки и запятую
                line = line.strip().strip(',').strip('"')
                if line:
                    content_lines.append(line)

            if not content_lines:
                logger.warning("⚠️ Найдена таблица, но строк не извлечено")
                return None

            logger.info(f"✅ Успешно загружено {len(content_lines)} строк из истории чата")
            return content_lines

        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке истории чата: {e}", exc_info=True)
            return None