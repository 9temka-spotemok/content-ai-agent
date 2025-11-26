@echo off
cd /d "%~dp0"
echo Starting Streamlit server...
start /B python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
timeout /t 6
echo Opening Opera GX...
start "" "opera-gx" "http://localhost:8501"
echo.
echo Project is running at http://localhost:8501
echo Press any key to exit...
pause >nul

