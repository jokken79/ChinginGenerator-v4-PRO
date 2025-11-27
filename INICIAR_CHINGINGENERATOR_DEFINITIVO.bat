@echo off
title ChinginGenerator v4-PRO - Iniciador DEFINITIVO
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║     CHINGINGENERATOR V4-PRO - SISTEMA DE NÓMINAS           ║
echo  ║     Versión DEFINITIVA con TODAS las Mejoras              ║
echo  ║                                                           ║
echo  ║     Características:                                         ║
echo  ║     ✓ Sin problemas de puerto                               ║
echo  ║     ✓ Sin mensajes en japonés                              ║
echo  ║     ✓ Interfaz mejorada con temas claro/oscuro          ║
echo  ║     ✓ Selector moderno/clásico en settings               ║
echo  ║     ✓ Agentes Claude integrados                          ║
echo  ║     ✓ Settings funcionales completos                        ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

python iniciar_chingin_definitivo.py

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ╔══════════════════════════════════════════════════════════════╗
    echo  ║     ERROR: No se pudo iniciar la aplicación               ║
    echo  ║     Verifique que Python esté instalado correctamente      ║
    echo  ║     O ejecute directamente: python app.py                   ║
    echo  ╚════════════════════════════════════════════════════════════╝
    echo.
    timeout /t 5 /nobreak >nul
) else (
    echo.
    echo  ╔════════════════════════════════════════════════════════════╗
    echo  ║     APLICACIÓN FINALIZADA CORRECTAMENTE                 ║
    echo  ║     Gracias por usar ChinginGenerator v4-PRO             ║
    echo  ╚════════════════════════════════════════════════════════════╝
    echo.
    timeout /t 3 /nobreak >nul
)