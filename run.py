#!/usr/bin/env python3
"""
賃金台帳 Generator v4 PRO - Launcher
"""
import webbrowser
import time
import threading

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
