
@echo off
cd /d "C:\Users\gilvan\Desktop\controle_notebooks"

".venv\Scripts\python.exe" -m waitress --listen=0.0.0.0:5000 app:app
