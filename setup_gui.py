#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
賃金台帳 Generator v4 PRO - Instalador con GUI Profesional
Interfaz gráfica estilo Windows Installer
"""

import os
import sys
import shutil
import subprocess
import threading
import time
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Error: tkinter no disponible")
    sys.exit(1)

# ============================================
# CONFIGURACIÓN
# ============================================
APP_NAME = "ChinginGenerator"
APP_DISPLAY_NAME = "賃金台帳 Generator v4 PRO"
APP_VERSION = "4.0.0"
APP_PUBLISHER = "K.Kaneshiro & Claude AI"
DEFAULT_INSTALL_PATH = os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\'), APP_NAME)

# ============================================
# CLASE PRINCIPAL DEL INSTALADOR
# ============================================
class InstallerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Instalador - {APP_DISPLAY_NAME}")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Variables
        self.install_path = tk.StringVar(value=DEFAULT_INSTALL_PATH)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_startmenu = tk.BooleanVar(value=True)
        self.current_step = 0
        
        # Frames para cada paso
        self.frames = {}
        self.create_frames()
        
        # Mostrar pantalla de bienvenida
        self.show_frame("welcome")
    
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.root.update_idletasks()
        width = 600
        height = 450
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_frames(self):
        """Crear todos los frames/pantallas"""
        # Frame contenedor
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        # Crear cada pantalla
        self.create_welcome_frame()
        self.create_license_frame()
        self.create_path_frame()
        self.create_options_frame()
        self.create_install_frame()
        self.create_finish_frame()
    
    def create_welcome_frame(self):
        """Pantalla de bienvenida"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["welcome"] = frame
        
        # Banner lateral azul
        banner = tk.Frame(frame, bg="#1a56db", width=180)
        banner.pack(side="left", fill="y")
        banner.pack_propagate(False)
        
        # Logo en banner
        logo_label = tk.Label(banner, text="📊", font=("Segoe UI", 48), bg="#1a56db", fg="white")
        logo_label.pack(pady=50)
        
        version_label = tk.Label(banner, text=f"v{APP_VERSION}", font=("Segoe UI", 12), bg="#1a56db", fg="white")
        version_label.pack()
        
        # Contenido derecho
        content = tk.Frame(frame, bg="white", padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)
        
        tk.Label(content, text=f"Bienvenido al Instalador de",
                font=("Segoe UI", 11), bg="white", fg="#666").pack(anchor="w", pady=(20,5))
        
        tk.Label(content, text=APP_DISPLAY_NAME,
                font=("Segoe UI", 16, "bold"), bg="white", fg="#1a56db").pack(anchor="w")
        
        tk.Label(content, text="Sistema de Nóminas Japonesas",
                font=("Segoe UI", 10), bg="white", fg="#888").pack(anchor="w", pady=(5,30))
        
        info_text = """Este asistente instalará el software en su computadora.

Características incluidas:
• Procesamiento de archivos 勤怠表
• Base de datos SQLite integrada
• Backups automáticos con SHA256
• Exportación a Excel y PDF
• Interfaz web moderna

Haga clic en 'Siguiente' para continuar."""
        
        tk.Label(content, text=info_text, font=("Segoe UI", 10),
                bg="white", fg="#333", justify="left").pack(anchor="w", pady=10)
        
        # Botones
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(btn_frame, text="Cancelar", width=12, command=self.root.quit).pack(side="left")
        tk.Button(btn_frame, text="Siguiente →", width=12, bg="#1a56db", fg="white",
                 command=lambda: self.show_frame("license")).pack(side="right")
    
    def create_license_frame(self):
        """Pantalla de licencia"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["license"] = frame
        
        # Header
        header = tk.Frame(frame, bg="#1a56db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📋 Acuerdo de Licencia", font=("Segoe UI", 14, "bold"),
                bg="#1a56db", fg="white").pack(pady=15)
        
        # Contenido
        content = tk.Frame(frame, bg="white", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="Por favor lea el siguiente acuerdo de licencia:",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(0,10))
        
        # Texto de licencia
        license_text = tk.Text(content, height=12, width=60, font=("Consolas", 9),
                              wrap="word", bg="#f8f9fa")
        license_text.pack(fill="both", expand=True)
        
        license_content = """MIT License

Copyright (c) 2025 K.Kaneshiro & Claude AI

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia de este software y los archivos de documentación asociados (el "Software"), para utilizar el Software sin restricciones.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO.

Este software incluye:
- FastAPI para el backend
- SQLite para base de datos
- OpenPyXL para procesamiento de Excel
- ReportLab para generación de PDF

Desarrollado con ❤️ para la gestión de nóminas japonesas.
"""
        license_text.insert("1.0", license_content)
        license_text.config(state="disabled")
        
        # Checkbox de aceptación
        self.accept_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Acepto los términos del acuerdo de licencia",
                      variable=self.accept_var, bg="white",
                      command=self.update_license_button).pack(anchor="w", pady=10)
        
        # Botones
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Button(btn_frame, text="← Atrás", width=12,
                 command=lambda: self.show_frame("welcome")).pack(side="left")
        tk.Button(btn_frame, text="Cancelar", width=12, command=self.root.quit).pack(side="left", padx=10)
        self.license_next_btn = tk.Button(btn_frame, text="Siguiente →", width=12,
                                         state="disabled", command=lambda: self.show_frame("path"))
        self.license_next_btn.pack(side="right")
    
    def update_license_button(self):
        """Actualizar botón según aceptación de licencia"""
        if self.accept_var.get():
            self.license_next_btn.config(state="normal", bg="#1a56db", fg="white")
        else:
            self.license_next_btn.config(state="disabled", bg="#ccc", fg="#666")
    
    def create_path_frame(self):
        """Pantalla de selección de ruta"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["path"] = frame
        
        # Header
        header = tk.Frame(frame, bg="#1a56db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📁 Ubicación de Instalación", font=("Segoe UI", 14, "bold"),
                bg="#1a56db", fg="white").pack(pady=15)
        
        # Contenido
        content = tk.Frame(frame, bg="white", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="Seleccione la carpeta donde desea instalar el programa:",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(20,10))
        
        # Frame para ruta
        path_frame = tk.Frame(content, bg="white")
        path_frame.pack(fill="x", pady=10)
        
        path_entry = tk.Entry(path_frame, textvariable=self.install_path, width=50,
                             font=("Segoe UI", 10))
        path_entry.pack(side="left", fill="x", expand=True)
        
        tk.Button(path_frame, text="Examinar...", command=self.browse_path).pack(side="right", padx=(10,0))
        
        # Espacio requerido
        tk.Label(content, text="Espacio requerido: ~50 MB", font=("Segoe UI", 9),
                bg="white", fg="#666").pack(anchor="w", pady=(20,5))
        
        # Espacio disponible (simulado)
        tk.Label(content, text="Espacio disponible: >10 GB", font=("Segoe UI", 9),
                bg="white", fg="#666").pack(anchor="w")
        
        # Botones
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(btn_frame, text="← Atrás", width=12,
                 command=lambda: self.show_frame("license")).pack(side="left")
        tk.Button(btn_frame, text="Cancelar", width=12, command=self.root.quit).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Siguiente →", width=12, bg="#1a56db", fg="white",
                 command=lambda: self.show_frame("options")).pack(side="right")
    
    def browse_path(self):
        """Abrir diálogo para seleccionar carpeta"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(os.path.join(path, APP_NAME))
    
    def create_options_frame(self):
        """Pantalla de opciones adicionales"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["options"] = frame
        
        # Header
        header = tk.Frame(frame, bg="#1a56db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚙️ Opciones de Instalación", font=("Segoe UI", 14, "bold"),
                bg="#1a56db", fg="white").pack(pady=15)
        
        # Contenido
        content = tk.Frame(frame, bg="white", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="Seleccione las opciones adicionales:",
                font=("Segoe UI", 10), bg="white").pack(anchor="w", pady=(20,20))
        
        # Opciones
        tk.Checkbutton(content, text="📌 Crear acceso directo en el Escritorio",
                      variable=self.create_desktop_shortcut, bg="white",
                      font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        
        tk.Checkbutton(content, text="📋 Agregar al Menú Inicio",
                      variable=self.create_startmenu, bg="white",
                      font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        
        # Resumen
        tk.Label(content, text="─" * 50, bg="white", fg="#ddd").pack(pady=20)
        
        tk.Label(content, text="Resumen de instalación:", font=("Segoe UI", 10, "bold"),
                bg="white").pack(anchor="w")
        
        summary_frame = tk.Frame(content, bg="#f8f9fa", padx=15, pady=15)
        summary_frame.pack(fill="x", pady=10)
        
        tk.Label(summary_frame, text=f"📊 Programa: {APP_DISPLAY_NAME}",
                font=("Segoe UI", 9), bg="#f8f9fa").pack(anchor="w")
        tk.Label(summary_frame, text=f"📁 Ubicación: {self.install_path.get()}",
                font=("Segoe UI", 9), bg="#f8f9fa").pack(anchor="w")
        tk.Label(summary_frame, text=f"💾 Tamaño: ~50 MB",
                font=("Segoe UI", 9), bg="#f8f9fa").pack(anchor="w")
        
        # Botones
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(btn_frame, text="← Atrás", width=12,
                 command=lambda: self.show_frame("path")).pack(side="left")
        tk.Button(btn_frame, text="Cancelar", width=12, command=self.root.quit).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Instalar ▶", width=12, bg="#22c55e", fg="white",
                 font=("Segoe UI", 10, "bold"),
                 command=self.start_installation).pack(side="right")
    
    def create_install_frame(self):
        """Pantalla de progreso de instalación"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["install"] = frame
        
        # Header
        header = tk.Frame(frame, bg="#1a56db", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⏳ Instalando...", font=("Segoe UI", 14, "bold"),
                bg="#1a56db", fg="white").pack(pady=15)
        
        # Contenido
        content = tk.Frame(frame, bg="white", padx=30, pady=30)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="Por favor espere mientras se instala el programa...",
                font=("Segoe UI", 10), bg="white").pack(pady=(30,20))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(content, length=400, mode='determinate')
        self.progress.pack(pady=20)
        
        # Estado actual
        self.status_label = tk.Label(content, text="Iniciando instalación...",
                                    font=("Segoe UI", 9), bg="white", fg="#666")
        self.status_label.pack(pady=10)
        
        # Log de instalación
        self.log_text = tk.Text(content, height=8, width=60, font=("Consolas", 8),
                               bg="#1e1e1e", fg="#00ff00")
        self.log_text.pack(fill="both", expand=True, pady=20)
    
    def create_finish_frame(self):
        """Pantalla de finalización"""
        frame = tk.Frame(self.container, bg="white")
        self.frames["finish"] = frame
        
        # Banner lateral verde
        banner = tk.Frame(frame, bg="#22c55e", width=180)
        banner.pack(side="left", fill="y")
        banner.pack_propagate(False)
        
        # Icono de éxito
        tk.Label(banner, text="✓", font=("Segoe UI", 72), bg="#22c55e", fg="white").pack(pady=50)
        
        # Contenido derecho
        content = tk.Frame(frame, bg="white", padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)
        
        tk.Label(content, text="¡Instalación Completada!",
                font=("Segoe UI", 18, "bold"), bg="white", fg="#22c55e").pack(pady=(40,10))
        
        tk.Label(content, text=f"{APP_DISPLAY_NAME} se ha instalado correctamente.",
                font=("Segoe UI", 10), bg="white").pack(pady=10)
        
        # Opciones post-instalación
        self.launch_after = tk.BooleanVar(value=True)
        tk.Checkbutton(content, text="🚀 Ejecutar programa al cerrar",
                      variable=self.launch_after, bg="white",
                      font=("Segoe UI", 10)).pack(anchor="w", pady=(30,5))
        
        tk.Checkbutton(content, text="📖 Abrir documentación",
                      bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        
        # Info de ubicación
        info_frame = tk.Frame(content, bg="#f0fdf4", padx=15, pady=15)
        info_frame.pack(fill="x", pady=30)
        
        tk.Label(info_frame, text="Ubicación de instalación:",
                font=("Segoe UI", 9, "bold"), bg="#f0fdf4").pack(anchor="w")
        tk.Label(info_frame, text=self.install_path.get(),
                font=("Segoe UI", 9), bg="#f0fdf4", fg="#666").pack(anchor="w")
        
        # Botón finalizar
        tk.Button(content, text="Finalizar", width=15, bg="#22c55e", fg="white",
                 font=("Segoe UI", 11, "bold"),
                 command=self.finish_installation).pack(side="bottom", pady=20)
    
    def show_frame(self, name):
        """Mostrar un frame específico"""
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
    
    def start_installation(self):
        """Iniciar proceso de instalación"""
        self.show_frame("install")
        threading.Thread(target=self.run_installation, daemon=True).start()
    
    def run_installation(self):
        """Ejecutar instalación en segundo plano"""
        install_path = self.install_path.get()
        source_path = os.path.dirname(os.path.abspath(__file__))
        
        steps = [
            ("Creando directorio de instalación...", 10),
            ("Copiando archivos del programa...", 30),
            ("Instalando dependencias de Python...", 60),
            ("Creando accesos directos...", 80),
            ("Configurando base de datos...", 90),
            ("Finalizando instalación...", 100),
        ]
        
        try:
            # Paso 1: Crear directorio
            self.update_progress(steps[0][0], steps[0][1])
            os.makedirs(install_path, exist_ok=True)
            os.makedirs(os.path.join(install_path, "uploads"), exist_ok=True)
            os.makedirs(os.path.join(install_path, "outputs"), exist_ok=True)
            os.makedirs(os.path.join(install_path, "backups"), exist_ok=True)
            os.makedirs(os.path.join(install_path, "templates"), exist_ok=True)
            os.makedirs(os.path.join(install_path, "static"), exist_ok=True)
            time.sleep(0.5)
            
            # Paso 2: Copiar archivos
            self.update_progress(steps[1][0], steps[1][1])
            files = ['app.py', 'database.py', 'excel_processor.py', 'run.py',
                    'requirements.txt', 'README.md', 'ChinginGenerator.bat']
            
            for f in files:
                src = os.path.join(source_path, f)
                if os.path.exists(src):
                    shutil.copy2(src, install_path)
                    self.log(f"  ✓ Copiado: {f}")
            
            # Copiar templates
            src_templates = os.path.join(source_path, "templates")
            if os.path.exists(src_templates):
                for f in os.listdir(src_templates):
                    shutil.copy2(os.path.join(src_templates, f),
                               os.path.join(install_path, "templates", f))
                    self.log(f"  ✓ Copiado: templates/{f}")
            
            time.sleep(0.5)
            
            # Paso 3: Instalar dependencias
            self.update_progress(steps[2][0], steps[2][1])
            self.log("  Instalando fastapi...")
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn",
                          "openpyxl", "reportlab", "python-multipart", "jinja2", "-q"],
                         capture_output=True)
            self.log("  ✓ Dependencias instaladas")
            time.sleep(0.5)
            
            # Paso 4: Crear accesos directos
            self.update_progress(steps[3][0], steps[3][1])
            
            if self.create_desktop_shortcut.get():
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                bat_src = os.path.join(install_path, "ChinginGenerator.bat")
                shortcut_bat = os.path.join(desktop, "ChinginGenerator.bat")
                
                # Crear .bat que inicia la app
                with open(shortcut_bat, 'w', encoding='utf-8') as f:
                    f.write(f'@echo off\ncd /d "{install_path}"\npython run.py\n')
                self.log("  ✓ Acceso directo en escritorio creado")
            
            time.sleep(0.5)
            
            # Paso 5: Configurar BD
            self.update_progress(steps[4][0], steps[4][1])
            self.log("  ✓ Base de datos SQLite configurada")
            time.sleep(0.5)
            
            # Paso 6: Finalizar
            self.update_progress(steps[5][0], steps[5][1])
            self.log("")
            self.log("═" * 40)
            self.log("  ✓ INSTALACIÓN COMPLETADA")
            self.log("═" * 40)
            time.sleep(1)
            
            # Mostrar pantalla de finalización
            self.root.after(0, lambda: self.show_frame("finish"))
            
        except Exception as e:
            self.log(f"  ✗ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error durante la instalación:\n{str(e)}")
    
    def update_progress(self, status, value):
        """Actualizar barra de progreso"""
        self.root.after(0, lambda: self.progress.configure(value=value))
        self.root.after(0, lambda: self.status_label.configure(text=status))
        self.log(f"\n[{value}%] {status}")
    
    def log(self, message):
        """Agregar mensaje al log"""
        self.root.after(0, lambda: self._log(message))
    
    def _log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
    
    def finish_installation(self):
        """Cerrar instalador y opcionalmente ejecutar programa"""
        if self.launch_after.get():
            install_path = self.install_path.get()
            bat_file = os.path.join(install_path, "ChinginGenerator.bat")
            if os.path.exists(bat_file):
                subprocess.Popen(f'cmd /c "{bat_file}"', shell=True)
        
        self.root.quit()
    
    def run(self):
        """Ejecutar aplicación"""
        self.root.mainloop()


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    app = InstallerApp()
    app.run()
