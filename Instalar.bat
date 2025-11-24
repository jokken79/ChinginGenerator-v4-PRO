@echo off
chcp 65001 > nul
title 賃金台帳 Generator v4 PRO - Instalador
color 1F

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║      賃金台帳 Generator v4 PRO                               ║
echo ║      INSTALADOR PROFESIONAL                                  ║
echo ║                                                              ║
echo ║      Sistema de Nominas Japonesas                            ║
echo ║      Version 4.0.0                                           ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
python --version > nul 2>&1
if errorlevel 1 (
    color 4F
    echo.
    echo  ╔═══════════════════════════════════════════════════════╗
    echo  ║  ERROR: Python no encontrado                          ║
    echo  ║                                                       ║
    echo  ║  Por favor instale Python desde:                      ║
    echo  ║  https://www.python.org/downloads/                    ║
    echo  ║                                                       ║
    echo  ║  Asegurese de marcar "Add Python to PATH"             ║
    echo  ╚═══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

echo  [OK] Python encontrado
echo.
echo  Iniciando instalador grafico...
echo.

:: Ejecutar instalador GUI
cd /d "%~dp0"
python setup.py

if errorlevel 1 (
    echo.
    echo  Hubo un error al ejecutar el instalador.
    echo  Intente ejecutar: python setup.py
    pause
)
