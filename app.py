#!/usr/bin/env python3
"""
賃金台帳 Generator v4 PRO - Web Application OPTIMIZADO
Sistema completo con base de datos, auditoría, backups y mejoras de performance
"""

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import re
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import threading
import time
from functools import lru_cache
import hashlib

from excel_processor import ExcelProcessor
from database import (
    init_database, get_statistics, get_audit_log,
    create_backup, get_backups, verify_backup_integrity,
    restore_from_backup, get_all_settings, set_setting,
    get_all_employees, get_all_payroll_records, get_periods,
    clear_all_data, sync_all_employees, sync_haken_employees,
    sync_ukeoi_employees, get_employee_master, get_employee_master_stats,
    get_all_haken_employees, get_all_ukeoi_employees,
    get_dispatch_companies, get_ukeoi_job_types,
    get_employees_by_company, get_employees_by_job_type
)

# Importar optimizaciones de performance
try:
    from performance_optimizations import (
        PerformanceCache,
        get_all_employees_cached,
        get_statistics_cached,
        get_periods_cached,
        bulk_insert_payroll_records,
        optimize_database_indexes,
        get_performance_metrics
    )
    PERFORMANCE_ENABLED = True
    print("[OK] Optimizaciones de performance cargadas")
except ImportError:
    PERFORMANCE_ENABLED = False
    print("ADVERTENCIA: Modulo de optimizaciones no encontrado, usando funciones originales")

# Importar agentes Claude para análisis avanzado
try:
    from claude_agents import (
        PayrollAnalyzerAgent,
        ReportGeneratorAgent,
        DataValidationAgent,
        TrendAnalysisAgent,
        AnomalyDetectionAgent,
        ComplianceAgent
    )
    AGENTS_ENABLED = True
    print("[OK] Agentes Claude Elite cargados y listos")
except ImportError:
    AGENTS_ENABLED = False
    print("ADVERTENCIA: Agentes Claude no encontrados, analisis avanzado no disponible")

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Inicializar cache de performance si está disponible
if PERFORMANCE_ENABLED:
    cache = PerformanceCache()
else:
    cache = None

# Inicializar app
app = FastAPI(
    title="賃金台帳 Generator v4 PRO - OPTIMIZADO",
    description="Sistema de Nóminas Japonesas con Base de Datos y Optimizaciones",
    version="4.1.0"
)

# Middleware mejorado para logging de performance y cache
@app.middleware("http")
async def enhanced_log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Log mejorado con indicadores de cache
    if duration > 0.5:
        print(f"[SLOW] {request.method} {request.url.path} took {duration:.2f}s")
    elif duration > 0.2:
        print(f"[NORMAL] {request.method} {request.url.path} took {duration:.2f}s")
    else:
        print(f"[FAST] {request.method} {request.url.path} took {duration:.3f}s")

    # Headers de debugging
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    if cache and hasattr(cache, 'cache_hits'):
        response.headers["X-Cache-Hits"] = str(cache.cache_hits)
        response.headers["X-Cache-Misses"] = str(cache.cache_misses)

    return response

# Static files y templates
if os.path.exists(os.path.join(BASE_DIR, "static")):
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
    """Página principal con estadísticas cacheadas - UI Moderna"""
    if PERFORMANCE_ENABLED:
        stats = get_statistics_cached()
    else:
        stats = get_statistics()
    
    # Detectar si se solicita UI clásica
    ui_theme = request.query_params.get("theme", "moderno")
    template_name = "index.html" if ui_theme == "clasico" else "index_moderno.html"
    
    return templates.TemplateResponse(template_name, {
        "request": request,
        "stats": stats
    })

@app.get("/theme/{theme}")
async def switch_theme(theme: str):
    """Cambiar tema de la interfaz"""
    if theme not in ["moderno", "clasico"]:
        raise HTTPException(status_code=400, detail="Tema no válido")
    
    # Redirigir a home con el tema seleccionado
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/?theme={theme}", status_code=302)


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
    """Obtener todos los datos con optimizaciones de cache"""
    # Usar funciones cacheadas si están disponibles
    if PERFORMANCE_ENABLED:
        employees = get_all_employees_cached()
        periods = get_periods_cached()
        stats = get_statistics_cached()
    else:
        employees = get_all_employees()
        periods = get_periods()
        stats = get_statistics()
    
    # Los records de payroll no se cachean porque cambian frecuentemente
    records = get_all_payroll_records()
    
    return JSONResponse({
        "records": records,
        "employees": employees,
        "periods": periods,
        "stats": stats,
        "cache_enabled": PERFORMANCE_ENABLED
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
# API - BÚSQUEDA Y GENERACIÓN POR EMPLEADO
# ========================================

@app.get("/api/employee/{employee_id}")
async def search_employee(employee_id: str):
    """Buscar informacion de un empleado por ID"""
    result = processor.search_employee(employee_id)
    return JSONResponse(result)


@app.get("/api/employee/{employee_id}/chingin")
async def generate_employee_chingin(employee_id: str, year: int = None):
    """Generar 賃金台帳 para un empleado específico en formato Print"""
    if year is None:
        year = datetime.now().year
    
    result = processor.generate_chingin_print(employee_id, year)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    # Devolver el archivo
    if result.get("output_path") and os.path.exists(result["output_path"]):
        filename = f"賃金台帳_{employee_id}_{year}.xlsx"
        return FileResponse(result["output_path"], filename=filename)
    
    return JSONResponse(result)


@app.get("/api/chingin/by-company/{company_name}")
async def generate_chingin_by_company(company_name: str, year: int = None):
    """Generar 賃金台帳 para todos los empleados de una fábrica (ZIP)"""
    import zipfile
    import io
    from urllib.parse import unquote
    
    if year is None:
        year = datetime.now().year
    
    company = unquote(company_name)
    employees = get_employees_by_company(company)
    
    if not employees.get('employees'):
        raise HTTPException(status_code=404, detail=f"No hay empleados en {company}")
    
    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    generated_count = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for emp in employees['employees']:
            emp_id = emp['id']
            try:
                result = processor.generate_chingin_print(emp_id, year)
                if result.get("output_path") and os.path.exists(result["output_path"]):
                    # Leer el archivo y agregarlo al ZIP
                    with open(result["output_path"], 'rb') as f:
                        filename = f"賃金台帳_{emp_id}_{emp['name']}_{year}.xlsx"
                        zip_file.writestr(filename, f.read())
                        generated_count += 1
            except Exception as e:
                print(f"Error generando para {emp_id}: {e}")
                continue
    
    if generated_count == 0:
        raise HTTPException(status_code=404, detail=f"No se pudieron generar archivos para {company}")
    
    zip_buffer.seek(0)

    filename_encoded = quote(f"賃金台帳_{company}_{year}.zip")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
    )


@app.get("/api/chingin/by-job-type/{job_type}")
async def generate_chingin_by_job_type(job_type: str, year: int = None):
    """Generar 賃金台帳 para todos los empleados de un tipo de trabajo (ZIP)"""
    import zipfile
    import io
    from urllib.parse import unquote
    
    if year is None:
        year = datetime.now().year
    
    jt = unquote(job_type)
    employees = get_employees_by_job_type(jt)
    
    if not employees.get('employees'):
        raise HTTPException(status_code=404, detail=f"No hay empleados en {jt}")
    
    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    generated_count = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for emp in employees['employees']:
            emp_id = emp['id']
            try:
                result = processor.generate_chingin_print(emp_id, year)
                if result.get("output_path") and os.path.exists(result["output_path"]):
                    # Leer el archivo y agregarlo al ZIP
                    with open(result["output_path"], 'rb') as f:
                        filename = f"賃金台帳_{emp_id}_{emp['name']}_{year}.xlsx"
                        zip_file.writestr(filename, f.read())
                        generated_count += 1
            except Exception as e:
                print(f"Error generando para {emp_id}: {e}")
                continue
    
    if generated_count == 0:
        raise HTTPException(status_code=404, detail=f"No se pudieron generar archivos para {jt}")
    
    zip_buffer.seek(0)

    filename_encoded = quote(f"賃金台帳_{jt}_{year}.zip")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
    )


@app.get("/api/chingin/all-ukeoi")
async def generate_chingin_all_ukeoi(year: int = None):
    """Generar 賃金台帳 para TODOS los empleados (派遣社員 + 請負社員) en ZIP"""
    import zipfile
    import io

    if year is None:
        year = datetime.now().year

    # Obtener TODOS los empleados (tanto 派遣社員 como 請負社員)
    employees = get_all_employees()

    if not employees:
        raise HTTPException(status_code=404, detail="No hay empleados registrados")

    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    generated_count = 0

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for emp in employees:
            emp_id = emp.get('employee_id')
            emp_name = emp.get('name_jp', emp.get('name_roman', ''))
            try:
                result = processor.generate_chingin_print(emp_id, year)
                if result.get("output_path") and os.path.exists(result["output_path"]):
                    with open(result["output_path"], 'rb') as f:
                        filename = f"賃金台帳_{emp_id}_{emp_name}_{year}.xlsx"
                        zip_file.writestr(filename, f.read())
                        generated_count += 1
            except Exception as e:
                print(f"Error generando para {emp_id}: {e}")
                continue

    if generated_count == 0:
        raise HTTPException(status_code=404, detail="No se pudieron generar archivos")

    zip_buffer.seek(0)

    filename_encoded = quote(f"賃金台帳_全員_{year}.zip")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
    )


@app.get("/api/employee/{employee_id}/chingin-v2")
async def generate_employee_chingin_v2(
    employee_id: str,
    year: int = None,
    format: str = "b",  # "b" o "c"
    output_type: str = "excel"  # "excel" o "pdf"
):
    """
    Generar 賃金台帳 usando Templates B o C, con opcion Excel o PDF

    Args:
        employee_id: ID del empleado
        year: Ano (default: ano actual)
        format: "b" para Template B (detallado) o "c" para Template C (simplificado)
        output_type: "excel" para archivo Excel o "pdf" para convertir a PDF
    """
    if year is None:
        year = datetime.now().year

    # Validar parametros
    if format not in ["b", "c"]:
        raise HTTPException(status_code=400, detail="Formato debe ser 'b' o 'c'")
    if output_type not in ["excel", "pdf"]:
        raise HTTPException(status_code=400, detail="output_type debe ser 'excel' o 'pdf'")

    # Generar archivo Excel segun formato
    if format == "b":
        result = processor.generate_chingin_format_b(employee_id, year)
    else:  # format == "c"
        result = processor.generate_chingin_format_c(employee_id, year)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    excel_path = result.get("file_path")
    if not excel_path or not os.path.exists(excel_path):
        raise HTTPException(status_code=500, detail="Error generando archivo Excel")

    # Si se solicita PDF, convertir
    if output_type == "pdf":
        pdf_result = processor.convert_excel_to_pdf(excel_path)

        if pdf_result["status"] == "error":
            # Si falla conversion a PDF, devolver Excel
            print(f"[WARN] Conversion a PDF fallo, devolviendo Excel: {pdf_result['message']}")
            filename_encoded = quote(f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.xlsx")
            return FileResponse(
                excel_path,
                filename=f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.xlsx",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
            )

        pdf_path = pdf_result.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            filename_encoded = quote(f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.pdf")
            return FileResponse(
                pdf_path,
                filename=f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.pdf",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
            )

    # Devolver Excel
    filename_encoded = quote(f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.xlsx")
    return FileResponse(
        excel_path,
        filename=f"賃金台帳_{employee_id}_{year}_Format{format.upper()}.xlsx",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"}
    )


@app.get("/api/employee/{employee_id}/preview")
async def preview_employee_chingin(employee_id: str, year: int = None):
    """Obtener vista previa de datos del empleado para 賃金台帳"""
    from database import get_payroll_by_employee
    
    if year is None:
        year = datetime.now().year
    
    records = get_payroll_by_employee(employee_id)
    
    if not records:
        raise HTTPException(status_code=404, detail=f"No se encontraron datos para {employee_id}")
    
    # Organizar por mes
    by_month = {}
    for rec in records:
        period = rec.get("period", "")
        match = re.search(r'(\d+)月', str(period))
        if match:
            month = int(match.group(1))
            by_month[month] = {
                "period": rec.get("period"),
                "work_days": rec.get("work_days"),
                "work_hours": rec.get("work_hours"),
                "overtime_hours": rec.get("overtime_hours"),
                "base_pay": rec.get("base_pay"),
                "overtime_pay": rec.get("overtime_pay"),
                "total_pay": rec.get("total_pay"),
                "deduction_total": rec.get("deduction_total"),
                "net_pay": rec.get("net_pay"),
            }
    
    return JSONResponse({
        "employee_id": employee_id,
        "name_jp": records[0].get('name_jp', ''),
        "name_roman": records[0].get('name_roman', ''),
        "year": year,
        "data_by_month": by_month
    })


# ========================================
# API - ESTADÍSTICAS
# ========================================

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas con cache"""
    if PERFORMANCE_ENABLED:
        stats = get_statistics_cached()
    else:
        stats = get_statistics()
    
    return JSONResponse(stats)


@app.get("/api/employees")
async def get_employees():
    """Obtener lista de empleados con cache"""
    if PERFORMANCE_ENABLED:
        employees = get_all_employees_cached()
    else:
        employees = get_all_employees()
    
    return JSONResponse(employees)


@app.get("/api/periods")
async def get_periods_list():
    """Obtener lista de periodos con cache"""
    if PERFORMANCE_ENABLED:
        periods = get_periods_cached()
    else:
        periods = get_periods()
    
    return JSONResponse(periods)


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


@app.post("/api/clear-all")
async def clear_all_database():
    """Borrar TODOS los datos de la base de datos"""
    # Primero crear un backup
    backup = create_backup('auto', 'Backup antes de borrar todos los datos')
    
    # Limpiar procesador
    processor.clear()
    
    # Limpiar archivos temporales
    for f in os.listdir(UPLOAD_DIR):
        try:
            os.remove(os.path.join(UPLOAD_DIR, f))
        except:
            pass
    
    # Borrar datos de BD
    result = clear_all_data()
    result['backup_created'] = backup.get('filename', 'error')
    
    return JSONResponse(result)


@app.post("/api/upload-with-progress")
async def upload_files_with_progress(files: List[UploadFile] = File(...)):
    """Subir y procesar archivos con progreso detallado (respuesta normal)"""
    results = []
    total_files = len(files)
    total_records = 0
    
    for idx, file in enumerate(files):
        file_result = {
            "filename": file.filename,
            "file_number": idx + 1,
            "total_files": total_files,
            "status": "processing"
        }
        
        if not file.filename.endswith(('.xlsm', '.xlsx', '.xls')):
            file_result["status"] = "error"
            file_result["message"] = "Formato no soportado"
            results.append(file_result)
            continue
        
        # Guardar archivo
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_result["step"] = "saved"
        file_result["size"] = len(content)
        
        # Procesar
        result = processor.process_file(filepath)
        
        file_result["status"] = result.get("status", "error")
        file_result["records"] = result.get("records", 0)
        total_records += result.get("records", 0)
        
        if result.get("status") == "error":
            file_result["message"] = result.get("message", "Error desconocido")
        
        results.append(file_result)
    
    return JSONResponse({
        "results": results,
        "summary": {
            "total_files": total_files,
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "total_records": total_records
        },
        "stats": get_statistics()
    })


@app.get("/api/health")
async def health_check():
    """Health check mejorado con métricas de performance"""
    if PERFORMANCE_ENABLED:
        stats = get_statistics_cached()
        metrics = get_performance_metrics()
    else:
        stats = get_statistics()
        metrics = {"cache_enabled": False}
    
    return JSONResponse({
        "status": "healthy",
        "version": "4.1.0",
        "performance_optimized": PERFORMANCE_ENABLED,
        "db_hash": stats['db_hash'][:16],
        "employees": stats['total_employees'],
        "records": stats['total_payroll_records'],
        **metrics
    })


# ========================================
# API - SINCRONIZACIÓN DE EMPLEADOS
# ========================================

@app.post("/api/sync-employees")
async def sync_employees():
    """Sincronizar empleados desde Excel maestro"""
    try:
        result = sync_all_employees()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/sync-haken")
async def sync_haken():
    """Sincronizar solo empleados 派遣社員"""
    try:
        result = sync_haken_employees()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/api/sync-ukeoi")
async def sync_ukeoi():
    """Sincronizar solo empleados 請負社員"""
    try:
        result = sync_ukeoi_employees()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/employee-master/{employee_id}")
async def get_employee_master_api(employee_id: str):
    """Obtener datos de empleado del maestro"""
    emp = get_employee_master(employee_id)
    if emp:
        return JSONResponse(emp)
    return JSONResponse({"error": "Empleado no encontrado"}, status_code=404)


@app.get("/api/employee-master-stats")
async def get_employee_stats():
    """Obtener estadísticas de empleados maestro"""
    return JSONResponse(get_employee_master_stats())


@app.get("/api/haken-employees")
async def get_haken_list():
    """Listar todos los empleados 派遣"""
    return JSONResponse(get_all_haken_employees())


@app.get("/api/ukeoi-employees")
async def get_ukeoi_list():
    """Listar todos los empleados 請負"""
    return JSONResponse(get_all_ukeoi_employees())


@app.get("/api/dispatch-companies")
async def get_companies():
    """Listar派遣先 (fábricas) únicas"""
    return JSONResponse(get_dispatch_companies())


@app.get("/api/job-types")
async def get_job_types():
    """Listar 請負業務 (tipos de trabajo) únicos"""
    return JSONResponse(get_ukeoi_job_types())


@app.get("/api/employees-by-company/{company_name}")
async def get_company_employees(company_name: str):
    """Listar empleados de una fábrica específica"""
    from urllib.parse import unquote
    company = unquote(company_name)
    return JSONResponse(get_employees_by_company(company))


@app.get("/api/employees-by-job-type/{job_type}")
async def get_job_type_employees(job_type: str):
    """Listar empleados de un tipo de trabajo específico"""
    from urllib.parse import unquote
    jt = unquote(job_type)
    return JSONResponse(get_employees_by_job_type(jt))


# Nuevos endpoints para gestión de cache y optimización

@app.get("/api/cache/clear")
async def clear_cache():
    """Limpiar cache de performance"""
    if PERFORMANCE_ENABLED and cache:
        cache.clear()
        return JSONResponse({
            "status": "ok",
            "message": "Cache limpiado",
            "cache_enabled": True
        })
    else:
        return JSONResponse({
            "status": "ok",
            "message": "Cache no disponible",
            "cache_enabled": False
        })

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Obtener estadísticas del cache"""
    if PERFORMANCE_ENABLED and cache:
        return JSONResponse({
            "cache_enabled": True,
            "cache_size": len(cache.cache),
            "cache_hits": cache.cache_hits,
            "cache_misses": cache.cache_misses,
            "hit_rate": cache.cache_hits / (cache.cache_hits + cache.cache_misses) if (cache.cache_hits + cache.cache_misses) > 0 else 0
        })
    else:
        return JSONResponse({
            "cache_enabled": False,
            "message": "Cache no disponible"
        })

@app.post("/api/optimize-db")
async def optimize_database():
    """Optimizar índices de la base de datos"""
    if PERFORMANCE_ENABLED:
        try:
            result = optimize_database_indexes()
            return JSONResponse({
                "status": "ok",
                "message": "Base de datos optimizada",
                "result": result
            })
        except Exception as e:
            return JSONResponse({
                "status": "error",
                "message": f"Error optimizando BD: {str(e)}"
            }, status_code=500)
    else:
        return JSONResponse({
            "status": "error",
            "message": "Optimización no disponible"
        }, status_code=501)

# ========================================
# API - AGENTES CLAUDE ELITE (ANÁLISIS AVANZADO)
# ========================================

@app.get("/api/agents/status")
async def get_agents_status():
    """Verificar estado de los agentes Claude"""
    return JSONResponse({
        "agents_enabled": AGENTS_ENABLED,
        "available_agents": [
            "PayrollAnalyzerAgent",
            "ReportGeneratorAgent",
            "DataValidationAgent",
            "TrendAnalysisAgent",
            "AnomalyDetectionAgent",
            "ComplianceAgent"
        ] if AGENTS_ENABLED else []
    })

@app.post("/api/agents/analyze-payroll")
async def analyze_payroll_data():
    """Analizar datos de nómina con agente especializado"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener datos
        if PERFORMANCE_ENABLED:
            employees = get_all_employees_cached()
            payroll_records = get_all_payroll_records()
        else:
            employees = get_all_employees()
            payroll_records = get_all_payroll_records()
        
        # Usar agente para análisis
        agent = PayrollAnalyzerAgent()
        analysis = agent.analyze_payroll_data(employees, payroll_records)
        
        return JSONResponse({
            "status": "ok",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error en análisis: {str(e)}"
        }, status_code=500)

@app.post("/api/agents/detect-anomalies")
async def detect_payroll_anomalies():
    """Detectar anomalías en datos de nómina"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener datos recientes
        payroll_records = get_all_payroll_records()
        
        # Usar agente de detección de anomalías
        agent = AnomalyDetectionAgent()
        anomalies = agent.detect_anomalies(payroll_records)
        
        return JSONResponse({
            "status": "ok",
            "anomalies": anomalies,
            "total_records": len(payroll_records),
            "anomaly_count": len(anomalies),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error detectando anomalías: {str(e)}"
        }, status_code=500)

@app.post("/api/agents/generate-report")
async def generate_intelligent_report(report_type: str = "monthly"):
    """Generar reporte inteligente con agente especializado"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener datos según tipo de reporte
        if PERFORMANCE_ENABLED:
            stats = get_statistics_cached()
            employees = get_all_employees_cached()
            periods = get_periods_cached()
        else:
            stats = get_statistics()
            employees = get_all_employees()
            periods = get_periods()
        
        payroll_records = get_all_payroll_records()
        
        # Usar agente generador de reportes
        agent = ReportGeneratorAgent()
        report = agent.generate_report(
            report_type=report_type,
            stats=stats,
            employees=employees,
            payroll_records=payroll_records,
            periods=periods
        )
        
        return JSONResponse({
            "status": "ok",
            "report": report,
            "report_type": report_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error generando reporte: {str(e)}"
        }, status_code=500)

@app.post("/api/agents/analyze-trends")
async def analyze_salary_trends():
    """Analizar tendencias salariales con agente especializado"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener datos históricos
        payroll_records = get_all_payroll_records()
        employees = get_all_employees()
        
        # Usar agente de análisis de tendencias
        agent = TrendAnalysisAgent()
        trends = agent.analyze_trends(payroll_records, employees)
        
        return JSONResponse({
            "status": "ok",
            "trends": trends,
            "data_points": len(payroll_records),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error analizando tendencias: {str(e)}"
        }, status_code=500)

@app.post("/api/agents/validate-data")
async def validate_payroll_data():
    """Validar integridad de datos con agente especializado"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener todos los datos
        employees = get_all_employees()
        payroll_records = get_all_payroll_records()
        periods = get_periods()
        
        # Usar agente de validación
        agent = DataValidationAgent()
        validation = agent.validate_data(employees, payroll_records, periods)
        
        return JSONResponse({
            "status": "ok",
            "validation": validation,
            "employees_count": len(employees),
            "records_count": len(payroll_records),
            "periods_count": len(periods),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error validando datos: {str(e)}"
        }, status_code=500)

@app.post("/api/agents/compliance-check")
async def check_compliance():
    """Verificar cumplimiento normativo japonés"""
    if not AGENTS_ENABLED:
        return JSONResponse({
            "status": "error",
            "message": "Agentes Claude no disponibles"
        }, status_code=501)
    
    try:
        # Obtener datos relevantes para cumplimiento
        employees = get_all_employees()
        payroll_records = get_all_payroll_records()
        
        # Usar agente de cumplimiento
        agent = ComplianceAgent()
        compliance = agent.check_japanese_compliance(employees, payroll_records)
        
        return JSONResponse({
            "status": "ok",
            "compliance": compliance,
            "employees_checked": len(employees),
            "records_checked": len(payroll_records),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error verificando cumplimiento: {str(e)}"
        }, status_code=500)

# Inicializar BD al arrancar con optimizaciones
@app.on_event("startup")
async def startup():
    init_database()
    
    # Optimizar base de datos si está disponible
    if PERFORMANCE_ENABLED:
        try:
            optimize_database_indexes()
            print("[OK] Base de datos optimizada con indices")
        except Exception as e:
            print(f"[ERROR] Error optimizando BD: {e}")
    
    # Limpiar archivos viejos al iniciar
    try:
        cleanup_old_files()
        print("[OK] Limpieza de archivos viejos completada")
    except Exception as e:
        print(f"[ERROR] Error en limpieza: {e}")
    
    print("[OK] Base de datos inicializada")
    print("[OK] ChinginApp v4.1 PRO OPTIMIZADO listo!")
    if PERFORMANCE_ENABLED:
        print("[OK] Optimizaciones de performance activadas")
    if AGENTS_ENABLED:
        print("[OK] Agentes Claude Elite activados para analisis avanzado")

def cleanup_old_files(days: int = 7, delete: bool = True):
    """Limpiar archivos viejos de uploads y outputs"""
    import glob
    from datetime import datetime
    
    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    # Limpiar uploads
    for pattern in ["uploads/*.xlsx", "uploads/*.xlsm", "uploads/*.xls"]:
        for filepath in glob.glob(os.path.join(BASE_DIR, pattern)):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_time:
                    if delete:
                        os.remove(filepath)
                        deleted_count += 1
                    else:
                        print(f"Would delete: {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    # Limpiar outputs (solo archivos temporales, no los .xlsx finales)
    for pattern in ["outputs/temp_*", "outputs/tmp_*"]:
        for filepath in glob.glob(os.path.join(BASE_DIR, pattern)):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_time:
                    if delete:
                        os.remove(filepath)
                        deleted_count += 1
                    else:
                        print(f"Would delete: {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    if delete:
        print(f"[INFO] Eliminados {deleted_count} archivos viejos")
    else:
        print(f"[INFO] Se eliminarian {deleted_count} archivos viejos")
    
    return deleted_count


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    import socket
    
    # Configurar logging para ejecutable
    if hasattr(sys, 'frozen') and getattr(sys, 'frozen', False):
        # Estamos corriendo como ejecutable
        import logging
        
        # Configurar logging básico sin caracteres especiales
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s:%(name)s:%(message)s'
        )
        
        # Buscar un puerto disponible
        port = 8000
        while port < 8100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    break
            except OSError:
                port += 1
        
        print(f"[INFO] Iniciando servidor en puerto {port}")
        
        # Configurar uvicorn sin logging complejo
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            access_log=False,
            log_config=None,
            log_level="critical"  # Solo errores críticos
        )
    else:
        # Estamos corriendo como script normal
        uvicorn.run(app, host="0.0.0.0", port=8000)
