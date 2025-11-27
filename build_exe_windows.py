#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear ejecutable .exe de ChinginGenerator v4.1 PRO
Compatible con Windows sin problemas de codificacion
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instalar PyInstaller si no esta disponible"""
    print("Verificando PyInstaller...")
    try:
        import PyInstaller
        print("[OK] PyInstaller ya esta instalado")
        return True
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller instalado correctamente")
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
        print(f"[ERROR] Archivos faltantes: {missing}")
        return False
    
    print("[OK] Todos los archivos necesarios encontrados")
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
    
    print("[OK] Dependencias instaladas")

def build_executable():
    """Construir el ejecutable"""
    print("Construyendo ejecutable...")
    
    # Comando PyInstaller para Windows
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=ChinginGenerator",
        "--add-data=templates;templates",
        "--windowed",
        "app.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] Ejecutable creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error construyendo ejecutable: {e}")
        return False

def create_distribution():
    """Crear paquete de distribucion"""
    print("Creando paquete de distribucion...")
    
    dist_dir = Path("ChinginGenerator_Dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copiar ejecutable
    exe_path = Path("dist/ChinginGenerator.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "ChinginGenerator.exe")
        print("[OK] Ejecutable copiado")
    else:
        print("[WARNING] No se encontro el ejecutable en dist/")
        return None
    
    # Copiar templates
    if os.path.exists("templates"):
        if os.path.exists(dist_dir / "templates"):
            shutil.rmtree(dist_dir / "templates")
        shutil.copytree("templates", dist_dir / "templates")
        print("[OK] Templates copiados")
    
    # Copiar archivos estaticos si existen
    if os.path.exists("static"):
        shutil.copytree("static", dist_dir / "static")
        print("[OK] Archivos estaticos copiados")
    
    # Crear script de inicio
    start_script = """@echo off
title ChinginGenerator v4.1 PRO - Interfaz Moderna
echo.
echo Iniciando ChinginGenerator v4.1 PRO...
echo.
echo Interfaz Moderna con Optimizaciones de Performance
echo.
echo Agentes Claude Elite Integrados
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
    
    print("[OK] Script de inicio creado")
    
    # Crear README
    readme = """# ChinginGenerator v4.1 PRO - Version Ejecutable

## Caracteristicas Principales

### Interfaz Moderna
- Glass Morphism con efectos blur y transparencias
- Gradientes animados y efectos neon
- Dashboard interactivo con estadisticas en tiempo real
- Drag & Drop moderno con feedback visual
- Terminal integrada para logs de procesamiento

### Optimizaciones de Performance
- Cache inteligente con TTL para datos maestros
- Indices optimizados en base de datos SQLite
- Bulk operations para inserciones masivas
- Logging mejorado con metricas de respuesta

### Agentes Claude Elite
- PayrollAnalyzerAgent - Analisis avanzado de nominas
- ReportGeneratorAgent - Reportes inteligentes automaticos
- DataValidationAgent - Validacion de integridad de datos
- TrendAnalysisAgent - Analisis de tendencias salariales
- AnomalyDetectionAgent - Deteccion de anomalias
- ComplianceAgent - Verificacion de cumplimiento normativo

## Uso

### Metodo 1: Ejecutar directamente
```
ChinginGenerator.exe
```

### Metodo 2: Script de inicio (Windows)
```
INICIAR.bat
```

### Metodo 3: Modo desarrollador
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
- Usa Ctrl+Shift+T para mostrar/ocultar el selector de tema
- Elige entre "Moderno" (recomendado) y "Clasico"
- La preferencia se guarda automaticamente

## Atajos de Teclado
- Ctrl+Shift+T: Mostrar/ocultar selector de tema
- F5: Actualizar pagina
- Ctrl+R: Recargar sin cache

## Archivos Incluidos

- ChinginGenerator.exe - Aplicacion principal
- templates/ - Todas las plantillas HTML
- static/ - Archivos estaticos (CSS, JS, imagenes)
- INICIAR.bat - Script de inicio para Windows
- README.md - Documentacion completa

## Configuracion

La aplicacion crea automaticamente:
- Base de datos SQLite en el directorio actual
- Directorios uploads/ y outputs/ para archivos
- Logs de auditoria y backup automaticos

---

Version: 4.1.0 PRO
Build: Ejecutable Windows con Interfaz Moderna
"""
    
    with open(dist_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("[OK] README creado")
    
    return dist_dir

def main():
    """Funcion principal"""
    print("=" * 60)
    print("Constructor de Ejecutable - ChinginGenerator v4.1 PRO")
    print("Interfaz Moderna + Optimizaciones + Agentes Claude Elite")
    print("=" * 60)
    
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
    
    if dist_dir:
        print("=" * 60)
        print("CONSTRUCCION COMPLETADA CON EXITO!")
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
        print()
        print("CARACTERISTICAS INCLUIDAS:")
        print("- Interfaz Moderna con Glass Morphism")
        print("- Optimizaciones de Performance")
        print("- Agentes Claude Elite Integrados")
        print("- Selector de Temas (Ctrl+Shift+T)")
        print("=" * 60)
        return True
    else:
        print("[ERROR] No se pudo crear el paquete de distribucion")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n[EXITO] Ejecutable creado correctamente.")
            print("Listo para distribuir y usar!")
        else:
            print("\n[ERROR] No se pudo crear el ejecutable.")
    except Exception as e:
        print(f"\n[ERROR] {e}")