#!/usr/bin/env python3
import subprocess
import time
import sys
import os

def test_executable():
    exe_path = "dist/ChinginGenerator.exe"
    
    if not os.path.exists(exe_path):
        print(f"ERROR: No se encuentra el ejecutable en {exe_path}")
        return False
    
    print(f"Iniciando prueba del ejecutable: {exe_path}")
    
    try:
        process = subprocess.Popen([exe_path])
        print("Esperando 5 segundos para que la aplicacion inicie...")
        time.sleep(5)
        
        if process.poll() is None:
            print("EXITO: El ejecutable esta corriendo correctamente")
            print("La aplicacion deberia estar accesible en: http://localhost:8000")
            
            response = input("\n¿Desea cerrar la aplicacion? (s/n): ").lower()
            if response == 's':
                process.terminate()
                print("Aplicacion cerrada")
            
            return True
        else:
            print("ERROR: El ejecutable se cerro inesperadamente")
            return False
            
    except Exception as e:
        print(f"ERROR al ejecutar: {e}")
        return False

if __name__ == "__main__":
    print("TEST DE EJECUTABLE - ChinginGenerator v4-PRO")
    print("=" * 50)
    
    success = test_executable()
    
    if success:
        print("\nTEST COMPLETADO EXITOSAMENTE")
        print("El ejecutable funciona correctamente y esta listo para distribucion")
    else:
        print("\nTEST FALLIDO")
        print("El ejecutable tiene problemas y necesita revision")
        sys.exit(1)