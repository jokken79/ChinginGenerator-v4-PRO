#!/usr/bin/env python3
"""
賃金台帳 Generator v4 PRO - Web Application
Sistema completo con base de datos, auditoría y backups
"""

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from datetime import datetime
from typing import List

from excel_processor import ExcelProcessor
from database import (
    init_database, get_statistics, get_audit_log,
    create_backup, get_backups, verify_backup_integrity,
    restore_from_backup, get_all_settings, set_setting,
    get_all_employees, get_all_payroll_records, get_periods
)

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Inicializar app
app = FastAPI(
    title="賃金台帳 Generator v4 PRO",
    description="Sistema de Nóminas Japonesas con Base de Datos",
    version="4.0.0"
)

# Static files y templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Procesador global
processor = ExcelProcessor()

# ========================================
# PÁGINAS
# ========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    stats = get_statistics()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })


# ========================================
# API - UPLOAD Y PROCESAMIENTO
# ========================================

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Subir y procesar archivos Excel"""
    results = []
    
    for file in files:
        if not file.filename.endswith(('.xlsm', '.xlsx', '.xls')):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Formato no soportado"
            })
            continue
        
        # Guardar archivo
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Procesar
        result = processor.process_file(filepath)
        results.append({
            "filename": file.filename,
            **result
        })
    
    return JSONResponse({
        "results": results,
        "summary": processor.get_summary()
    })


@app.get("/api/data")
async def get_data():
    """Obtener todos los datos"""
    return JSONResponse({
        "records": get_all_payroll_records(),
        "employees": get_all_employees(),
        "periods": get_periods(),
        "stats": get_statistics()
    })


@app.get("/api/summary")
async def get_summary():
    """Obtener resumen"""
    return JSONResponse(processor.get_summary())


# ========================================
# API - EXPORTACIÓN
# ========================================

@app.get("/api/export/all")
async def export_all():
    """Exportar Excel ALL consolidado"""
    filename = f"ALL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    processor.export_to_excel_all(filepath)
    return FileResponse(filepath, filename=filename)


@app.get("/api/export/monthly")
async def export_monthly():
    """Exportar Excel por mes"""
    filename = f"Por_mes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(OUTPUT_DIR, filename)
    processor.export_by_month(filepath)
    return FileResponse(filepath, filename=filename)


@app.get("/api/export/chingin")
async def export_chingin():
    """Exportar 賃金台帳 por empleado (ZIP)"""
    folder = os.path.join(OUTPUT_DIR, f"chingin_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    files = processor.export_chingin_by_employee(folder)
    
    # Crear ZIP
    zip_path = shutil.make_archive(folder, 'zip', folder)
    return FileResponse(zip_path, filename=os.path.basename(zip_path))


# ========================================
# API - ESTADÍSTICAS
# ========================================

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas"""
    return JSONResponse(get_statistics())


@app.get("/api/employees")
async def get_employees():
    """Obtener lista de empleados"""
    return JSONResponse(get_all_employees())


@app.get("/api/periods")
async def get_periods_list():
    """Obtener lista de periodos"""
    return JSONResponse(get_periods())


# ========================================
# API - AUDITORÍA
# ========================================

@app.get("/api/audit")
async def get_audit(limit: int = 50, action: str = None):
    """Obtener log de auditoría"""
    logs = get_audit_log(limit, action)
    return JSONResponse(logs)


# ========================================
# API - BACKUP Y RESTAURACIÓN
# ========================================

@app.post("/api/backup")
async def create_backup_endpoint(description: str = None):
    """Crear backup manual"""
    backup = create_backup('manual', description or 'Backup manual desde UI')
    return JSONResponse(backup)


@app.get("/api/backups")
async def get_backups_list():
    """Obtener lista de backups"""
    return JSONResponse(get_backups())


@app.post("/api/backup/{backup_id}/verify")
async def verify_backup(backup_id: int):
    """Verificar integridad de backup"""
    result = verify_backup_integrity(backup_id)
    return JSONResponse(result)


@app.post("/api/backup/{backup_id}/restore")
async def restore_backup(backup_id: int):
    """Restaurar desde backup"""
    result = restore_from_backup(backup_id)
    return JSONResponse(result)


# ========================================
# API - CONFIGURACIÓN
# ========================================

@app.get("/api/settings")
async def get_settings():
    """Obtener configuraciones"""
    return JSONResponse(get_all_settings())


@app.post("/api/settings/{key}")
async def update_setting(key: str, value: str):
    """Actualizar configuración"""
    set_setting(key, value)
    return JSONResponse({"status": "ok", "key": key, "value": value})


# ========================================
# API - UTILIDADES
# ========================================

@app.post("/api/clear")
async def clear_session():
    """Limpiar datos de sesión"""
    processor.clear()
    
    # Limpiar archivos temporales
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    
    return JSONResponse({"status": "ok", "message": "Sesión limpiada"})


@app.get("/api/health")
async def health_check():
    """Health check"""
    stats = get_statistics()
    return JSONResponse({
        "status": "healthy",
        "version": "4.0.0",
        "db_hash": stats['db_hash'][:16],
        "employees": stats['total_employees'],
        "records": stats['total_payroll_records']
    })


# Inicializar BD al arrancar
@app.on_event("startup")
async def startup():
    init_database()
    print("✓ Base de datos inicializada")
    print("✓ ChinginApp v4 PRO listo!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8989)
