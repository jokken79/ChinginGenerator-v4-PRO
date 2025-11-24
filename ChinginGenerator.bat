@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     賃金台帳 Generator v4 PRO                            ║
echo ║     Iniciando servidor...                                ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
python run.py
pause
