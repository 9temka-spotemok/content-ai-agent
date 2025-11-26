@echo off
chcp 65001 >nul
title Content AI Agent - Запуск
color 0A

echo.
echo ========================================
echo   Content AI Agent - Запуск в Opera GX
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Проверка файлов...
if not exist "streamlit_app.py" (
    echo ОШИБКА: streamlit_app.py не найден!
    pause
    exit /b 1
)
echo OK: Файлы найдены
echo.

echo [2/3] Запуск Streamlit сервера...
start "Streamlit Server" /MIN python -m streamlit run streamlit_app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false
echo OK: Сервер запускается...
echo.

echo [3/3] Ожидание запуска (6 секунд)...
timeout /t 6 /nobreak >nul

echo Открываю Opera GX...
start "" "opera-gx" "http://localhost:8501"

echo.
echo ========================================
echo   Проект запущен!
echo ========================================
echo.
echo URL: http://localhost:8501
echo.
echo Сервер работает в фоновом режиме
echo Для остановки закройте окно "Streamlit Server"
echo.
pause

