#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     賃金台帳 Generator v4 PRO                                ║
║     INSTALADOR PROFESIONAL                                   ║
║                                                              ║
║     Desarrollado por: K.Kaneshiro & Claude AI                ║
║     Versión: 4.0.0                                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Ejecute este archivo para instalar el programa.
"""

import os
import sys

# Verificar versión de Python
if sys.version_info < (3, 8):
    print("Error: Se requiere Python 3.8 o superior")
    print(f"Versión actual: {sys.version}")
    input("Presione Enter para salir...")
    sys.exit(1)

# Verificar tkinter
try:
    import tkinter
except ImportError:
    print("Error: tkinter no está disponible")
    print("Por favor reinstale Python con la opción 'tcl/tk and IDLE'")
    input("Presione Enter para salir...")
    sys.exit(1)

# Ejecutar instalador GUI
if __name__ == "__main__":
    from setup_gui import InstallerApp
    app = InstallerApp()
    app.run()
