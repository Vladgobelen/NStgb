#!/usr/bin/env python3
import subprocess
import time


def get_wow_window():
    """Находит окно WoW"""
    result = subprocess.run(
        "wmctrl -l | grep -i 'world of warcraft' | head -1 | awk '{print $1}'",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main():
    print("🔍 Тест отправки команды в WoW (новая последовательность)")
    print("==========================================================")

    # 1. Найти окно
    window_id = get_wow_window()
    if not window_id:
        print("❌ Окно WoW не найдено!")
        return
    print(f"✅ Окно найдено: {window_id}")

    # 2. Активировать окно
    print("🔄 Активация окна...")
    subprocess.run(f"wmctrl -i -R {window_id}", shell=True)
    time.sleep(0.1)
    print("✅ Окно активировано")

    # 3. Сначала Enter (открыть чат)
    print("⏎ Enter #1 (открыть чат)...")
    subprocess.run("xte 'key Return'", shell=True)
    time.sleep(0.1)
    print("✅ Чат открыт")

    # 4. Копировать текст в буфер
    test_text = "/run gpEnTg()"
    print(f"📋 Копирование в буфер: {test_text}")
    subprocess.run(f'echo -n "{test_text}" | xclip -selection clipboard', shell=True)
    time.sleep(0.1)
    print("✅ Текст в буфере")

    # 5. Вставить (Ctrl+V)
    print("📥 Вставка (Ctrl+V)...")
    subprocess.run("xdotool key ctrl+v", shell=True)
    time.sleep(0.1)
    print("✅ Текст вставлен")

    # 6. Enter (выполнить команду)
    print("⏎ Enter #2 (выполнить)...")
    subprocess.run("xte 'key Return'", shell=True)
    time.sleep(0.1)
    print("✅ Команда отправлена")

    print("")
    print("🏁 Тест завершён! Проверь чат WoW")


if __name__ == "__main__":
    main()
