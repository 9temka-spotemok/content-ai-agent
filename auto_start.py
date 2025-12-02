import subprocess
import time
import os
import sys

# Переходим в папку скрипта
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Запуск Content AI Agent...")
print("=" * 60)

# Запускаем Streamlit в новом окне
print("📡 Запускаю Streamlit сервер...")
streamlit_process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
     "--server.headless", "true",
     "--browser.gatherUsageStats", "false",
     "--server.port", "8501"],
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
)

print("⏳ Ожидание запуска сервера (6 секунд)...")
time.sleep(6)

print("🌐 Открываю Opera GX...")
url = "http://localhost:8501"

# Пробуем открыть Opera GX
try:
    subprocess.Popen(["start", "opera-gx", url], shell=True)
except:
    try:
        subprocess.Popen(["opera-gx", url])
    except:
        print(f"⚠️ Не удалось открыть Opera GX автоматически")
        print(f"Пожалуйста, откройте вручную: {url}")

print("=" * 60)
print(f"✅ Проект запущен!")
print(f"📱 URL: {url}")
print("=" * 60)
print("\n💡 Сервер работает в отдельном окне")
print("🛑 Для остановки закройте окно Streamlit")

