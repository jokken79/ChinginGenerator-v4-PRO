#!/usr/bin/env python3
"""
Script de prueba para verificar que el ejecutable funciona correctamente
"""
import subprocess
import time
import sys
import os

def test_executable():
    """Probar que el ejecutable inicie correctamente"""
    exe_path = "dist/ChinginGenerator.exe"
    
    if not os.path.exists(exe_path):
        print(f"ERROR: No se encuentra el ejecutable en {exe_path}")
        return False
    
    print(f"Iniciando prueba del ejecutable: {exe_path}")
    
    try:
        # Iniciar el ejecutable
        process = subprocess.Popen([exe_path],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
        
        print("Esperando 5 segundos para que la aplicación inicie...")
        time.sleep(5)
        
        # Verificar si el proceso sigue corriendo
        if process.poll() is None:
            print("EXITO: El ejecutable está corriendo correctamente")
            print("La aplicación debería estar accesible en: http://localhost:8000")
            
            # Preguntar si queremos cerrar la aplicación
            response = input("\n¿Desea cerrar la aplicación? (s/n): ").lower()
            if response == 's':
                process.terminate()
                print("Aplicación cerrada")
            
            return True
        else:
            # Si el proceso ya terminó, mostrar el error
            stdout, stderr = process.communicate()
            print("ERROR: El ejecutable se cerró inesperadamente")
            if stderr:
                print(f"Error: {stderr}")
            if stdout:
                print(f"Salida: {stdout}")
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
        print("El ejecutable funciona correctamente y está listo para distribución")
    else:
        print("\nTEST FALLIDO")
        print("El ejecutable tiene problemas y necesita revisión")
        sys.exit(1)