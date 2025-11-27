#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para crear ejecutable .exe de ChinginGenerator v4.1 PRO
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    print("Verificando PyInstaller...")
    try:
        import PyInstaller
        print("✓ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller instalado correctamente")
        return True

def check_files():
    """Verificar archivos necesarios"""
    print("Verificando archivos necesarios...")
    
    required_files = [
        "app.py",
        "templates/index_moderno.html",
        "templates/index.html", 
        "database.py",
        "excel_processor.py",
        "performance_optimizations.py"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"✗ Archivos faltantes: {missing}")
        return False
    
    print("✓ Todos los archivos necesarios encontrados")
    return True

def install_dependencies():
    """Instalar dependencias necesarias"""
    print("Instalando dependencias...")
    
    deps = [
        "fastapi",
        "uvicorn[standard]", 
        "jinja2",
        "openpyxl",
        "python-multipart",
        "aiofiles"
    ]
    
    for dep in deps:
        print(f"Instalando {dep}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✓ Dependencias instaladas")

def build_executable():
    """Construir el ejecutable"""
    print("Construyendo ejecutable...")
    
    # Comando PyInstaller simplificado
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=ChinginGenerator",
        "--add-data=templates;templates",
        "app.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Ejecutable creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error construyendo ejecutable: {e}")
        return False

def create_distribution():
    """Crear paquete de distribución"""
    print("Creando paquete de distribución...")
    
    dist_dir = Path("ChinginGenerator_Dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copiar ejecutable
    exe_path = Path("dist/ChinginGenerator.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "ChinginGenerator.exe")
        print("✓ Ejecutable copiado")
    
    # Copiar templates
    if os.path.exists("templates"):
        shutil.copytree("templates", dist_dir / "templates")
        print("✓ Templates copiados")
    
    # Copiar archivos estáticos si existen
    if os.path.exists("static"):
        shutil.copytree("static", dist_dir / "static")
        print("✓ Archivos estáticos copiados")
    
    # Crear script de inicio
    start_script = """@echo off
title ChinginGenerator v4.1 PRO - Interfaz Moderna
echo.
echo Iniciando ChinginGenerator v4.1 PRO...
echo.
echo Interfaz Moderna con Optimizaciones
echo.
echo Servidor web: http://localhost:8989
echo.
echo Presiona Ctrl+C para detener
echo.
cd /d "%~dp0"
ChinginGenerator.exe
pause
"""
    
    with open(dist_dir / "INICIAR.bat", 'w', encoding='utf-8') as f:
        f.write(start_script)
    
    print("✓ Script de inicio creado")
    
    # Crear README
    readme = """# ChinginGenerator v4.1 PRO - Version Ejecutable

## Caracteristicas Principales

### Interfaz Moderna
- Glass Morphism con efectos blur
- Gradientes animados y efectos neon
- Dashboard interactivo
- Drag & Drop moderno
- Terminal integrada para logs

### Optimizaciones de Performance
- Cache inteligente TTL
- Indices optimizados SQLite
- Bulk operations
- Logging mejorado

### Uso

#### Metodo 1: Ejecutar directamente
```
ChinginGenerator.exe
```

#### Metodo 2: Script de inicio (Windows)
```
INICIAR.bat
```

#### Metodo 3: Modo desarrollador
```
python app.py
```

## Acceso Web

Una vez iniciado, la aplicacion estara disponible en:
- URL Principal: http://localhost:8989
- Interfaz Moderna: http://localhost:8989?theme=moderno
- Interfaz Clasica: http://localhost:8989?theme=clasico

## Personalizacion

### Selector de Tema
- Usa Ctrl+Shift+T para mostrar/ocultar selector de tema
- Elige entre "Moderno" (recomendado) y "Clasico"
- La preferencia se guarda automaticamente

## Atajos de Teclado
- Ctrl+Shift+T: Mostrar/ocultar selector de tema
- F5: Actualizar pagina
- Ctrl+R: Recargar sin cache

---

Version: 4.1.0 PRO
Build: Ejecutable Windows
"""
    
    with open(dist_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("✓ README creado")
    
    return dist_dir

def main():
    """Funcion principal"""
    print("=" * 50)
    print("Constructor de Ejecutable - ChinginGenerator v4.1 PRO")
    print("=" * 50)
    
    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Paso 2: Verificar archivos
    if not check_files():
        return False
    
    # Paso 3: Instalar dependencias
    install_dependencies()
    
    # Paso 4: Construir ejecutable
    if not build_executable():
        return False
    
    # Paso 5: Crear distribucion
    dist_dir = create_distribution()
    
    print("=" * 50)
    print("¡CONSTRUCCION COMPLETADA!")
    print(f"Directorio de distribucion: {dist_dir.absolute()}")
    print()
    print("Archivos incluidos:")
    print("- ChinginGenerator.exe (aplicacion principal)")
    print("- templates/ (interfaces moderna y clasica)")
    print("- static/ (recursos estaticos)")
    print("- INICIAR.bat (script de inicio)")
    print("- README.md (documentacion)")
    print()
    print("Para ejecutar:")
    print("1. Ve al directorio ChinginGenerator_Dist")
    print("2. Ejecuta INICIAR.bat o ChinginGenerator.exe")
    print("3. Abre http://localhost:8989 en tu navegador")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n¡EXITO! Ejecutable creado correctamente.")
        else:
            print("\nERROR: No se pudo crear el ejecutable.")
    except Exception as e:
        print(f"\nERROR: {e}")