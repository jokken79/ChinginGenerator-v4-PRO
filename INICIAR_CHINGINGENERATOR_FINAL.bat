@echo off
title ChinginGenerator v4-PRO - Iniciador Final
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║     CHINGINGENERATOR V4-PRO - SISTEMA DE NÓMINAS           ║
echo  ║     Versión FINAL con Solución Definitiva                   ║
echo  ║                                                           ║
echo  ║     Iniciando aplicación web SIN CONFLICTOS DE PUERTO...     ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

python iniciar_app_final.py

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ╔══════════════════════════════════════════════════════════════╗
    echo  ║     ERROR: No se pudo iniciar la aplicación               ║
    echo  ║     Verifique que Python esté instalado correctamente      ║
    echo  ║     O ejecute directamente: python app.py                   ║
    echo  ╚══════════════════════════════════════════════════════════════╝
    echo.
    timeout /t 5 /nobreak >nul
) else (
    echo.
    echo  ╔════════════════════════════════════════════════════════════╗
    echo  ║     APLICACIÓN FINALIZADA CORRECTAMENTE                 ║
    echo  ║     Gracias por usar ChinginGenerator v4-PRO             ║
    echo  ╚══════════════════════════════════════════════════════════════╝
    echo.
    timeout /t 3 /nobreak >nul
)