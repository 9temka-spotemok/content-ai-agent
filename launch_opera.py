"""
Скрипт для запуска проекта в браузере Opera GX
"""
import subprocess
import time
import webbrowser
import os
import sys

def find_opera_gx():
    """Поиск Opera GX на системе"""
    possible_paths = [
        r"C:\Users\{}\AppData\Local\Programs\Opera GX\opera.exe".format(os.getenv('USERNAME')),
        r"C:\Program Files\Opera GX\opera.exe",
        r"C:\Program Files (x86)\Opera GX\opera.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Пробуем найти через реестр или просто используем opera-gx
    return "opera-gx"

def main():
    print("🚀 Запуск Content AI Agent...")
    print("=" * 60)
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("streamlit_app.py"):
        print("❌ Ошибка: streamlit_app.py не найден!")
        print("Убедитесь, что вы запускаете скрипт из папки content-ai-agent/")
        sys.exit(1)
    
    # Запускаем Streamlit в фоновом режиме
    print("📡 Запускаю Streamlit сервер...")
    
    try:
        # Запускаем streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", 
             "--server.headless", "true", 
             "--browser.gatherUsageStats", "false",
             "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Ждем немного, чтобы сервер запустился
        print("⏳ Ожидание запуска сервера...")
        time.sleep(5)
        
        # Проверяем, запустился ли сервер
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        
        if result == 0:
            print("✅ Сервер запущен на http://localhost:8501")
            
            # Открываем в Opera GX
            print("🌐 Открываю в Opera GX...")
            url = "http://localhost:8501"
            
            # Пробуем найти Opera GX
            opera_path = find_opera_gx()
            
            try:
                if os.path.exists(opera_path):
                    subprocess.Popen([opera_path, url])
                else:
                    # Пробуем через webbrowser
                    webbrowser.get('opera').open(url)
            except:
                # Если не получилось, пробуем просто открыть через webbrowser
                webbrowser.open(url)
            
            print("=" * 60)
            print("✅ Проект запущен!")
            print(f"📱 URL: {url}")
            print("=" * 60)
            print("\nДля остановки нажмите Ctrl+C")
            
            # Ждем завершения процесса
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Остановка сервера...")
                process.terminate()
                process.wait()
                print("✅ Сервер остановлен")
        else:
            print("❌ Сервер не запустился. Проверьте логи выше.")
            process.terminate()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

