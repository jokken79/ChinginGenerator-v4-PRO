#!/usr/bin/env python3
"""
Script final para iniciar ChinginGenerator v4-PRO
Solución definitiva al problema de puertos ocupados
"""
import sys
import os
import socket
import subprocess
import time
import webbrowser
from threading import Timer

def encontrar_puerto_disponible(puerto_inicial=8001):
    """Buscar un puerto disponible desde puerto_inicial hasta 8100"""
    puerto = puerto_inicial
    while puerto < 8100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', puerto))
                s.listen(1)
                return puerto
        except OSError:
            print(f"Puerto {puerto} ocupado, probando siguiente...")
            puerto += 1
    return puerto_inicial  # Si no encuentra disponible, devuelve el original

def abrir_navegador(url, delay=3):
    """Abrir navegador después de un retraso"""
    Timer(delay, lambda: webbrowser.open(url)).start()

def main():
    print("=" * 60)
    print("CHINGINGENERATOR V4-PRO - INICIADOR FINAL")
    print("=" * 60)
    
    # Verificar si estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("ERROR: No se encuentra app.py. Ejecutar desde el directorio del proyecto.")
        print("El programa se cerrara en 5 segundos...")
        time.sleep(5)
        return
    
    # Encontrar puerto disponible (empezando desde 8001 para evitar conflicto)
    puerto = encontrar_puerto_disponible(8001)
    print(f"INFO: Puerto disponible encontrado: {puerto}")
    
    # Iniciar la aplicación
    print(f"INFO: Iniciando ChinginGenerator v4-PRO en puerto {puerto}...")
    print(f"INFO: Acceso web: http://localhost:{puerto}")
    print(f"INFO: Abriendo navegador automaticamente en 3 segundos...")
    print(f"INFO: Presione Ctrl+C para detener el servidor")
    print("-" * 60)
    
    # Programar apertura del navegador
    abrir_navegador(f"http://localhost:{puerto}")
    
    try:
        # Usar el mismo Python que ejecuta este script
        python_exe = sys.executable
        cmd = [python_exe, 'app.py']
        
        # Configurar variables de entorno para el puerto
        env = os.environ.copy()
        env['PORT'] = str(puerto)
        
        # Iniciar el proceso
        process = subprocess.Popen(cmd, env=env)
        
        print(f"EXITO: ChinginGenerator iniciado correctamente!")
        print(f"ACCESO: Abriendo navegador en http://localhost:{puerto}")
        print("INFO: Espere unos segundos mientras se carga la aplicacion...")
        print("-" * 60)
        
        # Esperar a que el proceso termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\nINFO: Deteniendo servidor...")
        if 'process' in locals():
            process.terminate()
        print("INFO: Servidor detenido")
        print("El programa se cerrara en 2 segundos...")
        time.sleep(2)
    except Exception as e:
        print(f"ERROR: No se pudo iniciar la aplicación: {e}")
        print("El programa se cerrara en 5 segundos...")
        time.sleep(5)

if __name__ == "__main__":
    main()