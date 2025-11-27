@echo off
title ChinginGenerator v4-PRO - Iniciador Rápido
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║     CHINGINGENERATOR V4-PRO - SISTEMA DE NÓMINAS           ║
echo  ║     Versión OPTIMIZADA con Interfaz Moderna              ║
echo  ║                                                           ║
echo  ║     Iniciando aplicación web...                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

python iniciar_app.py

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ╔══════════════════════════════════════════════════════════════╗
    echo  ║     ERROR: No se pudo iniciar la aplicación               ║
    echo  ║     Verifique que Python esté instalado correctamente      ║
    echo  ╚════════════════════════════════════════════════════════════╝
    echo.
    pause
) else (
    echo.
    echo  ╔════════════════════════════════════════════════════════════╗
    echo  ║     APLICACIÓN INICIADA CORRECTAMENTE                  ║
    echo  ║     Acceda desde su navegador web                        ║
    echo  ╚══════════════════════════════════════════════════════════╝
    echo.
)