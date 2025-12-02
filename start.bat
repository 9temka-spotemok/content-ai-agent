@echo off
chcp 65001 >nul
echo 🚀 Запуск Content AI Agent...
echo ====================================

cd /d "%~dp0"

echo 📡 Запускаю Streamlit сервер...
start /B python -m streamlit run streamlit_app.py --server.headless true --browser.gatherUsageStats false --server.port 8501

timeout /t 5 /nobreak >nul

echo ✅ Сервер запущен на http://localhost:8501
echo 🌐 Открываю в Opera GX...

start "" "opera-gx" "http://localhost:8501"

echo ====================================
echo ✅ Проект запущен!
echo 📱 URL: http://localhost:8501
echo ====================================
echo.
echo Для остановки закройте это окно или нажмите Ctrl+C
pause

