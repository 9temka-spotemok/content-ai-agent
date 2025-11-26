"""
Быстрый запуск проекта в Opera GX
"""
import subprocess
import time
import os
import sys

def main():
    print("=" * 60)
    print("🚀 Запуск Content AI Agent в Opera GX")
    print("=" * 60)
    
    # Переходим в папку проекта
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n📡 Запускаю Streamlit сервер...")
    
    # Запускаем streamlit
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app.py",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.port", "8501"
    ]
    
    print(f"Команда: {' '.join(streamlit_cmd)}")
    
    try:
        # Запускаем в фоне
        process = subprocess.Popen(
            streamlit_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        print("⏳ Ожидание запуска сервера (5 секунд)...")
        time.sleep(5)
        
        print("\n✅ Сервер должен быть запущен!")
        print("🌐 Открываю Opera GX...")
        
        # Открываем Opera GX
        url = "http://localhost:8501"
        
        # Пробуем разные способы открыть Opera GX
        opera_commands = [
            ["opera-gx", url],
            ["start", "opera-gx", url],
            ["cmd", "/c", "start", "opera-gx", url]
        ]
        
        opened = False
        for cmd in opera_commands:
            try:
                subprocess.Popen(cmd, shell=True)
                opened = True
                break
            except:
                continue
        
        if not opened:
            print(f"\n⚠️ Не удалось открыть Opera GX автоматически")
            print(f"Пожалуйста, откройте вручную: {url}")
        
        print("\n" + "=" * 60)
        print(f"✅ Проект запущен!")
        print(f"📱 URL: {url}")
        print("=" * 60)
        print("\n💡 Для остановки закройте окно Streamlit или нажмите Ctrl+C")
        print("\n⏳ Ожидание... (нажмите Enter для выхода)")
        
        input()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка...")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

