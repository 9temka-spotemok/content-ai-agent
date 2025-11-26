@echo off
cd /d "%~dp0"
echo Starting Streamlit...
start /B python -m streamlit run streamlit_app.py --server.headless true --server.port 8501
timeout /t 5
start opera-gx http://localhost:8501
echo Project is running at http://localhost:8501
pause

