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
