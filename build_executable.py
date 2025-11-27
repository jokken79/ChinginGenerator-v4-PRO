#!/usr/bin/env python3
"""
Script para crear ejecutable .exe de 賃金台帳 Generator v4.1 PRO
Con interfaz moderna, optimizaciones y agentes Claude Elite
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def create_executable():
    """Crear ejecutable .exe con todas las optimizaciones"""
    
    print("🚀 Creando ejecutable para 賃金台帳 Generator v4.1 PRO")
    print("=" * 60)
    
    # Verificar dependencias
    print("📦 Verificando dependencias...")
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller no encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado")
    
    # Verificar archivos necesarios
    required_files = [
        "app.py",
        "templates/index_moderno.html",
        "templates/index.html",
        "templates/selector_tema.html",
        "database.py",
        "excel_processor.py",
        "performance_optimizations.py",
        "claude_agents.py" if os.path.exists("claude_agents.py") else None,
        "requirements_updated.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if file and not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Todos los archivos necesarios encontrados")
    
    # Crear directorio de build
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)
    
    # Crear spec file para PyInstaller
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher_used = None
cert_used = None

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static' if os.path.exists('static') else None),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    upx_dir=None,
    upx_exclude=[],
    upx_include=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    name='ChinginGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    uac_admin=False,
    uac_uiaccess=False,
    version='4.1.0',
    description='賃金台帳 Generator v4.1 PRO - Sistema de Nóminas Japonesas con Interfaz Moderna y Optimizaciones de Performance',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

pyz = PYZ(a, scripts=[],
    exe=EXE(pz, name='ChinginGenerator', debug=False, bootloader_ignore_signals=False, strip=False, upx_dir=None, upx_exclude=None, console=True, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None, version='4.1.0', description='賃金台帳 Generator v4.1 PRO - Sistema de Nóminas Japonesas con Interfaz Moderna y Optimizaciones de Performance', icon='icon.ico' if os.path.exists('icon.ico') else None),
)

coll = COLLECT(
    exe=EXE(name='ChinginGenerator', debug=False, bootloader_ignore_signals=False, strip=False, upx_dir=None, upx_exclude=None, console=True, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None, version='4.1.0', description='賃金台帳 Generator v4.1 PRO - Sistema de Nóminas Japonesas con Interfaz Moderna y Optimizaciones de Performance', icon='icon.ico' if os.path.exists('icon.ico') else None),
    strip=False,
    upx_dir=None,
    console=True,
    upx_exclude=None,
    name='ChinginGenerator',
    version='4.1.0',
    description='賃金台帳 Generator v4.1 PRO - Sistema de Nóminas Japonesas con Interfaz Moderna y Optimizaciones de Performance',
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx_dir=None,
    upx_exclude=None,
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('ChinginGenerator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")
    
    # Instalar dependencias adicionales
    print("📦 Instalando dependencias adicionales...")
    additional_deps = [
        "fastapi",
        "uvicorn[standard]",
        "jinja2",
        "openpyxl",
        "python-multipart",
        "aiofiles"
    ]
    
    for dep in additional_deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✅ Dependencias instaladas")
    
    # Construir el ejecutable
    print("🔨 Construyendo ejecutable...")
    build_commands = [
        [sys.executable, "-m", "PyInstaller", "--clean", "ChinginGenerator.spec"],
        [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--name=ChinginGenerator", "app.py"]
    ]
    
    for cmd in build_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=build_dir)
            print(f"✅ Comando ejecutado: {' '.join(cmd)}")
            if result.returncode == 0:
                print("✅ Build exitoso")
            else:
                print(f"⚠️ Build con advertencias: {result.stderr}")
        except Exception as e:
            print(f"❌ Error en build: {e}")
    
    # Verificar si se creó el ejecutable
    exe_path = build_dir / "dist" / "ChinginGenerator.exe"
    if exe_path.exists():
        file_size = exe_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print("=" * 60)
        print("🎉 ¡EJECUTABLE CREADO EXITOSAMENTE!")
        print(f"📍 Ubicación: {exe_path.absolute()}")
        print(f"📏 Tamaño: {size_mb:.1f} MB")
        print("=" * 60)
        
        # Crear directorio de distribución
        dist_dir = Path("ChinginGenerator_Dist")
        dist_dir.mkdir(exist_ok=True)
        
        # Copiar ejecutable y archivos necesarios
        shutil.copy2(exe_path, dist_dir / "ChinginGenerator.exe")
        
        # Copiar templates
        if os.path.exists("templates"):
            shutil.copytree("templates", dist_dir / "templates")
        
        # Copiar archivos estáticos
        if os.path.exists("static"):
            shutil.copytree("static", dist_dir / "static")
        
        # Copiar archivos de configuración
        config_files = [
            "requirements.txt",
            "requirements_updated.txt",
            "README.md",
            "OPTIMIZACIONES_V4.1.md",
            "INTERFAZ_MODERNA.md"
        ]
        
        for file in config_files:
            if os.path.exists(file):
                shutil.copy2(file, dist_dir / file)
        
        # Crear script de inicio
        start_script = f'''@echo off
title 賃金台帳 Generator v4.1 PRO - Modern UI
echo.
echo 🚀 Iniciando 賃金台帳 Generator v4.1 PRO...
echo.
echo 📊 Interfaz Moderna con Optimizaciones de Performance
echo.
echo 🤖 Agentes Claude Elite Integrados
echo.
echo 🌐 Servidor web iniciándose en http://localhost:8989
echo.
echo 📂 Presiona Ctrl+C para detener
echo.
echo.
cd /d "%~dp0"
ChinginGenerator.exe
pause
'''
        
        with open(dist_dir / "INICIAR.bat", 'w', encoding='utf-8') as f:
            f.write(start_script)
        
        print("✅ Directorio de distribución creado:")
        print(f"📁 {dist_dir.absolute()}")
        print("📄 INICIAR.bat - Script de inicio para Windows")
        
        # Crear README para distribución
        readme_content = f'''# 賃金台帳 Generator v4.1 PRO - Versión Ejecutable

## 🚀 Características Principales

### 🎨 Interfaz Moderna
- Glass Morphism con efectos de blur y transparencias
- Gradientes animados y efectos neón
- Dashboard interactivo con estadísticas en tiempo real
- Drag & Drop moderno con feedback visual
- Terminal integrada para logs de procesamiento

### ⚡ Optimizaciones de Performance
- Cache inteligente con TTL para datos maestros
- Índices optimizados en base de datos SQLite
- Bulk operations para inserciones masivas
- Logging mejorado con métricas de respuesta

### 🤖 Agentes Claude Elite
- PayrollAnalyzerAgent - Análisis avanzado de nóminas
- ReportGeneratorAgent - Reportes inteligentes automáticos
- DataValidationAgent - Validación de integridad de datos
- TrendAnalysisAgent - Análisis de tendencias salariales
- AnomalyDetectionAgent - Detección de anomalías
- ComplianceAgent - Verificación de cumplimiento normativo

## 🎮 Uso

### Método 1: Ejecutar directamente
```bash
ChinginGenerator.exe
```

### Método 2: Script de inicio (Windows)
```bash
INICIAR.bat
```

### Método 3: Modo desarrollador
```bash
python app.py
```

## 🌐 Acceso Web

Una vez iniciado, la aplicación estará disponible en:
- **URL Principal:** http://localhost:8989
- **Interfaz Moderna:** http://localhost:8989?theme=moderno
- **Interfaz Clásica:** http://localhost:8989?theme=clasico

## 🎨 Personalización

### Selector de Tema
- Usa **Ctrl+Shift+T** para mostrar/ocultar el selector de tema
- Elige entre "Moderno" (recomendado) y "Clásico"
- La preferencia se guarda automáticamente

### Atajos de Teclado
- **Ctrl+Shift+T:** Mostrar/ocultar selector de tema
- **F5:** Actualizar página
- **Ctrl+R:** Recargar sin caché

## 📁 Archivos Incluidos

- `ChinginGenerator.exe` - Aplicación principal
- `templates/` - Todas las plantillas HTML
- `static/` - Archivos estáticos (CSS, JS, imágenes)
- `requirements.txt` - Dependencias Python
- `README.md` - Documentación completa

## 🔧 Configuración

La aplicación crea automáticamente:
- Base de datos SQLite en el directorio actual
- Directorios `uploads/` y `outputs/` para archivos
- Logs de auditoría y backup automáticos

## 📞 Soporte

Para problemas o preguntas:
- Revisa la documentación en `README.md`
- Verifica los logs en la consola de la aplicación
- Asegúrate de tener Python 3.8+ instalado

---

**🎉 ¡Disfruta de la experiencia de nóminas más moderna y optimizada!**

*Versión: 4.1.0 PRO*
*Build: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
'''
        
        with open(dist_dir / "README_EXECUTABLE.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("=" * 60)
        print("🎉 ¡CONSTRUCCIÓN COMPLETA!")
        print("📁 Directorio de distribución:")
        print(f"   {dist_dir.absolute()}")
        print("📄 Archivos incluidos:")
        print("   ✅ ChinginGenerator.exe - Aplicación principal")
        print("   ✅ templates/ - Interfaz moderna y clásica")
        print("   ✅ static/ - Recursos estáticos")
        print("   ✅ INICIAR.bat - Script de inicio")
        print("   ✅ README_EXECUTABLE.md - Documentación")
        print("=" * 60)
        print("🚀 Ejecuta ChinginGenerator.exe para comenzar!")
        
        return True
    else:
        print("❌ No se encontró el ejecutable generado")
        return False

def create_icon():
    """Crear icono para la aplicación"""
    try:
        # Intentar crear un icono simple usando PIL
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear imagen 256x256
        img = Image.new('RGBA', (256, 256), (66, 126, 234, 255))
        draw = ImageDraw.Draw(img)
        
        # Dibujar fondo circular
        draw.ellipse([128, 128], 120, 120, fill=(102, 126, 234, 255))
        
        # Dibujar texto
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Texto principal
        text = "賃"
        bbox = draw.textbbox(text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = (256 - text_width) // 2
        text_y = (256 - text_height) // 2 - 40
        
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        # Texto secundario
        text2 = "台帳"
        bbox2 = draw.textbbox(text2, font=font)
        text2_width = bbox2[2] - bbox2[0]
        text2_height = bbox2[3] - bbox2[1]
        
        text2_x = (256 - text2_width) // 2
        text2_y = (256 - text2_height) // 2 + 20
        
        draw.text((text2_x, text2_y), text2, fill=(255, 255, 255), font=font)
        
        # Guardar como ICO
        img.save('icon.ico', format='ICO', sizes=[(256, 256)])
        print("✅ Icono creado: icon.ico")
        
    except ImportError:
        print("⚠️ PIL no disponible, omitiendo creación de icono...")
    except Exception as e:
        print(f"⚠️ Error creando icono: {e}")

if __name__ == "__main__":
    print("🔨 Constructor de Ejecutable - 賃金台帳 Generator v4.1 PRO")
    print("📋 Características:")
    print("   🎨 Interfaz Moderna con Glass Morphism")
    print("   ⚡ Optimizaciones de Performance")
    print("   🤖 Agentes Claude Elite Integrados")
    print("   📦 Empaquetado como .exe para Windows")
    print()
    
    # Crear icono
    create_icon()
    
    # Crear ejecutable
    success = create_executable()
    
    if success:
        print("\n🎉 ¡LISTO PARA DISTRIBUIR!")
        print("📁 Revisa el directorio 'ChinginGenerator_Dist'")
        print("🚀 Ejecuta 'INICIAR.bat' o 'ChinginGenerator.exe'")
    else:
        print("\n❌ Error en la construcción. Revisa los mensajes arriba.")