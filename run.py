#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
賃金台帳 Generator v4 PRO - Launcher
"""
import sys
import io
import webbrowser
import time
import threading

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:8989')

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     📊 賃金台帳 Generator v4 PRO                         ║
    ║     Sistema de Nóminas Japonesas con Base de Datos       ║
    ║                                                          ║
    ║     URL: http://localhost:8989                           ║
    ║     Presiona Ctrl+C para detener                         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Abrir navegador en segundo plano
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8989,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
