@echo off
cd /d "%~dp0"
if not exist .venv (
    uv venv
)
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
uv run streamlit run app.py
pause
