#!/usr/bin/env python3
"""
Versión SEGURA de app.py con autenticación, rate limiting y optimizaciones
Integra todas las mejoras de seguridad y performance
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import os
import logging
from typing import List, Dict, Any, Optional

# Importar módulos de seguridad y performance
from auth import AuthManager, get_current_user, get_current_active_user, require_admin, init_auth_db
from rate_limiter import rate_limit_middleware
from performance_optimizations import (
    bulk_insert_payroll_records,
    get_all_employees_cached,
    get_dispatch_companies_cached,
    get_statistics_cached,
    optimize_database_indexes,
    get_performance_metrics
)

# Importar módulos originales
from database import init_database, log_audit, check_auto_backup
from excel_processor import ExcelProcessor

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chingin_secure.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="賃金台帳 Generator v4 PRO - Secure",
    description="Sistema de Nóminas Japonesas con Seguridad y Performance Optimizada",
    version="4.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de seguridad y performance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://trusted-domain.com"],  # Configurar dominios permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware personalizado de rate limiting y performance logging
@app.middleware("http")
async def security_and_performance_middleware(request: Request, call_next):
    # Rate limiting
    try:
        await rate_limit_middleware(request, call_next)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": "Rate limit exceeded", "detail": e.detail}
        )
    
    # Performance logging
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log de requests lentos
    if duration > 0.5:
        logger.warning(f"⚠️ SLOW REQUEST: {request.method} {request.url.path} took {duration:.3f}s")
    elif duration > 0.2:
        logger.info(f"📊 REQUEST: {request.method} {request.url.path} took {duration:.3f}s")
    
    # Headers de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Eventos de startup
@app.on_event("startup")
async def startup_event():
    """Inicialización segura al arrancar la aplicación"""
    logger.info("🚀 Starting ChinginGenerator v4 PRO - Secure")
    
    # Inicializar base de datos
    init_database()
    
    # Inicializar sistema de autenticación
    init_auth_db()
    
    # Optimizar base de datos
    optimize_database_indexes()
    
    # Verificar backup automático
    check_auto_backup()
    
    logger.info("✅ Startup completed successfully")

# Templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================================
# ENDPOINTS PÚBLICOS (Sin autenticación)
# ================================

@app.get("/")
async def root(request: Request):
    """Página principal con login"""
    return templates.TemplateResponse("index_secure.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Health check público para monitoreo"""
    try:
        stats = get_statistics_cached()
        metrics = get_performance_metrics()
        
        return {
            "status": "healthy",
            "version": "4.1.0",
            "timestamp": time.time(),
            "database": {
                "connected": True,
                "records": stats.get("total_payroll_records", 0),
                "employees": stats.get("total_employees", 0)
            },
            "performance": {
                "cache_size": metrics["cache_stats"],
                "uptime": time.time()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

@app.post("/api/auth/login")
async def login(credentials: Dict[str, str]):
    """Endpoint de login"""
    try:
        username = credentials.get("username")
        password = credentials.get("password")
        
        user = AuthManager.authenticate_user(username, password)
        if not user:
            log_audit('LOGIN_FAILED', 'users', username, None, "Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Generar token
        access_token = AuthManager.create_access_token(
            data={"sub": user["username"], "role": user.get("role", "user")}
        )
        
        log_audit('LOGIN_SUCCESS', 'users', username, None, "Login successful")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": user["username"],
                "role": user.get("role", "user")
            }
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# ENDPOINTS PROTEGIDOS (Requieren autenticación)
# ================================

@app.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_active_user)):
    """Estadísticas del sistema (protegido)"""
    try:
        stats = get_statistics_cached()
        return JSONResponse(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

@app.post("/api/upload")
async def upload_files_secure(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Upload seguro de archivos con validación"""
    try:
        # Validar tamaño y cantidad de archivos
        MAX_FILES = 10
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        
        if len(files) > MAX_FILES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Maximum {MAX_FILES} files allowed"
            )
        
        total_size = 0
        for file in files:
            if file.size and file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File {file.filename} exceeds maximum size of 10MB"
                )
            total_size += file.size or 0
        
        if total_size > 50 * 1024 * 1024:  # 50MB total
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Total upload size exceeds 50MB"
            )
        
        # Validar tipos de archivo
        ALLOWED_EXTENSIONS = {'.xlsx', '.xlsm', '.xls'}
        
        processor = ExcelProcessor()
        results = []
        
        for file in files:
            # Validar extensión
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_ext} not allowed"
                )
            
            # Guardar archivo temporal
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file.filename)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Procesar archivo
            result = processor.process_file(file_path)
            results.append(result)
            
            # Limpiar archivo temporal
            os.remove(file_path)
        
        # Log de auditoría
        log_audit(
            'UPLOAD_FILES', 
            'uploads', 
            current_user["username"],
            len(files),
            f"Uploaded {len(files)} files successfully"
        )
        
        return {
            "status": "success",
            "results": results,
            "uploaded_by": current_user["username"],
            "total_files": len(files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        log_audit(
            'UPLOAD_ERROR', 
            'uploads', 
            current_user["username"],
            None,
            str(e)
        )
        raise HTTPException(status_code=500, detail="Error processing files")

@app.get("/api/employees")
async def get_employees_secure(current_user: dict = Depends(get_current_active_user)):
    """Obtener empleados con cache"""
    try:
        employees = get_all_employees_cached()
        return JSONResponse({"employees": employees})
    except Exception as e:
        logger.error(f"Employees error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving employees")

@app.get("/api/dispatch-companies")
async def get_companies_secure(current_user: dict = Depends(get_current_active_user)):
    """Obtener compañías de despacho con cache"""
    try:
        companies = get_dispatch_companies_cached()
        return JSONResponse({"companies": companies})
    except Exception as e:
        logger.error(f"Companies error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving companies")

# ================================
# ENDPOINTS DE ADMINISTRADOR
# ================================

@app.get("/api/admin/performance")
async def get_performance_metrics_admin(admin_user: dict = Depends(require_admin)):
    """Métricas de performance (solo admin)"""
    try:
        metrics = get_performance_metrics()
        return JSONResponse(metrics)
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics")

@app.post("/api/admin/clear-cache")
async def clear_cache_admin(admin_user: dict = Depends(require_admin)):
    """Limpiar caches (solo admin)"""
    try:
        from performance_optimizations import clear_all_caches
        clear_all_caches()
        
        log_audit(
            'CLEAR_CACHE', 
            'system', 
            admin_user["username"],
            None,
            "All caches cleared by admin"
        )
        
        return {"status": "success", "message": "All caches cleared"}
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail="Error clearing cache")

# ================================
# ENDPOINTS DE EXPORTACIÓN (Protegidos)
# ================================

@app.get("/api/export/all")
async def export_all_secure(current_user: dict = Depends(get_current_active_user)):
    """Exportar todos los datos (protegido)"""
    try:
        processor = ExcelProcessor()
        output_path = "outputs/ALL_secure.xlsx"
        processor.export_to_excel_all(output_path)
        
        log_audit(
            'EXPORT_ALL', 
            'exports', 
            current_user["username"],
            None,
            "Exported all data"
        )
        
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="chingin_all_secure.xlsx"
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail="Error exporting data")

# ================================
# MANEJO DE ERRORES
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador personalizado de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador general de excepciones"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "path": request.url.path,
            "timestamp": time.time()
        }
    )

# ================================
# EJECUCIÓN
# ================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🛡️ 賃金台帳 Generator v4 PRO - SECURE              ║
    ║     Sistema de Nóminas con Seguridad y Performance       ║
    ║                                                          ║
    ║     URL: http://localhost:8989                           ║
    ║     Docs: http://localhost:8989/docs                     ║
    ║     Presiona Ctrl+C para detener                         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app_v2_secure:app",
        host="0.0.0.0",
        port=8989,
        reload=False,
        log_level="info",
        ssl_keyfile=None,  # Configurar para HTTPS en producción
        ssl_certfile=None   # Configurar para HTTPS en producción
    )