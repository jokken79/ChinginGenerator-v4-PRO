#!/usr/bin/env python3
"""
Script simple para iniciar ChinginGenerator v4-PRO
Sin necesidad de ejecutable, inicia directamente el servidor
"""
import sys
import os
import socket
import subprocess
import time

def encontrar_puerto_disponible(puerto_inicial=8000):
    """Buscar un puerto disponible desde puerto_inicial hasta 8100"""
    puerto = puerto_inicial
    while puerto < 8100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', puerto))
                return puerto
        except OSError:
            puerto += 1
    return puerto_inicial  # Si no encuentra disponible, devuelve el original

def main():
    print("=" * 60)
    print("CHINGINGENERATOR V4-PRO - INICIADOR RAPIDO")
    print("=" * 60)
    
    # Verificar si estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("ERROR: No se encuentra app.py. Ejecutar desde el directorio del proyecto.")
        input("Presione Enter para salir...")
        return
    
    # Encontrar puerto disponible
    puerto = encontrar_puerto_disponible()
    print(f"INFO: Puerto disponible encontrado: {puerto}")
    
    # Iniciar la aplicación
    print(f"INFO: Iniciando ChinginGenerator v4-PRO en puerto {puerto}...")
    print(f"INFO: Acceso web: http://localhost:{puerto}")
    print(f"INFO: Presione Ctrl+C para detener el servidor")
    print("-" * 60)
    
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
        print(f"ACCESO: Abra su navegador y vaya a http://localhost:{puerto}")
        print("-" * 60)
        
        # Esperar a que el proceso termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\nINFO: Deteniendo servidor...")
        if 'process' in locals():
            process.terminate()
        print("INFO: Servidor detenido")
    except Exception as e:
        print(f"ERROR: No se pudo iniciar la aplicación: {e}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()