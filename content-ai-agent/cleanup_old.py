"""
Скрипт для удаления старой папки content_ai_agent из корня
Запустите этот скрипт из корневой папки E:\ИИшка\
"""
import shutil
import os
from pathlib import Path

# Путь к старой папке (относительно корня E:\ИИшка\)
old_folder = Path("../content_ai_agent")

if old_folder.exists():
    try:
        shutil.rmtree(old_folder)
        print(f"✅ Папка {old_folder} удалена")
    except Exception as e:
        print(f"⚠️ Ошибка при удалении: {e}")
        print("Папка содержит только кэш файлы (__pycache__), это не критично")
else:
    print(f"✅ Папка {old_folder} не найдена (уже удалена)")

print("\n✅ Очистка завершена!")
print("Проект находится в папке: content-ai-agent/")

