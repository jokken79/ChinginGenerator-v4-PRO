#!/usr/bin/env python3
"""
Rate Limiting para 賃金台帳 Generator v4 PRO
Implementa límites de requests por IP y usuario
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
import time

# Configuración
RATE_LIMIT_STORAGE = {}
DEFAULT_WINDOW = 60  # segundos
DEFAULT_LIMITS = {
    "upload": "10/minute",      # 10 uploads por minuto
    "export": "30/minute",      # 30 exports por minuto  
    "search": "100/minute",     # 100 búsquedas por minuto
    "default": "60/minute",     # 60 requests genéricos por minuto
}

class MemoryRateLimiter:
    """Rate limiter simple en memoria para desarrollo"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Verifica si request está permitido"""
        now = time.time()
        
        # Limpiar requests viejos
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < window
            ]
        else:
            self.requests[key] = []
        
        # Verificar límite
        if len(self.requests[key]) >= limit:
            return False
        
        # Registrar request actual
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Obtener requests restantes"""
        now = time.time()
        
        if key not in self.requests:
            return limit
        
        # Contar requests en ventana
        recent_count = sum(
            1 for req_time in self.requests[key]
            if now - req_time < window
        )
        
        return max(0, limit - recent_count)

# Instancia global
memory_limiter = MemoryRateLimiter()

# Configurar SlowAPI
limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler para rate limit exceeded"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": 60  # segundos
        }
    )

def check_rate_limit(request: Request, endpoint_type: str = "default") -> bool:
    """
    Verifica rate limit para request actual
    
    Args:
        request: Request de FastAPI
        endpoint_type: Tipo de endpoint (upload, export, search, default)
    
    Returns:
        True si permitido, False si excedido
    """
    # Obtener configuración
    rate_config = DEFAULT_LIMITS.get(endpoint_type, DEFAULT_LIMITS["default"])
    limit_str = rate_config.split("/")[0]
    window_str = rate_config.split("/")[1]
    
    limit = int(limit_str)
    if window_str == "minute":
        window = 60
    elif window_str == "hour":
        window = 3600
    else:
        window = int(window_str)
    
    # Key basado en IP
    client_ip = get_remote_address(request)
    key = f"{client_ip}:{endpoint_type}"
    
    # Verificar límite
    allowed = memory_limiter.is_allowed(key, limit, window)
    
    if not allowed:
        remaining = memory_limiter.get_remaining(key, limit, window)
        print(f"⚠️ RATE LIMIT: {client_ip} excedió {endpoint_type} (remaining: {remaining})")
    
    return allowed

# Decoradores para endpoints específicos
def rate_limit_upload(request: Request):
    """Rate limit para endpoints de upload"""
    return check_rate_limit(request, "upload")

def rate_limit_export(request: Request):
    """Rate limit para endpoints de export"""
    return check_rate_limit(request, "export")

def rate_limit_search(request: Request):
    """Rate limit para endpoints de búsqueda"""
    return check_rate_limit(request, "search")

def rate_limit_default(request: Request):
    """Rate limit para endpoints genéricos"""
    return check_rate_limit(request, "default")

# Middleware de FastAPI para rate limiting
async def rate_limit_middleware(request: Request, call_next):
    """Middleware que aplica rate limiting basado en path"""
    path = request.url.path
    
    # Determinar tipo de endpoint
    if "/upload" in path:
        if not rate_limit_upload(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many upload requests. Maximum 10 per minute."
            )
    elif "/export" in path:
        if not rate_limit_export(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many export requests. Maximum 30 per minute."
            )
    elif "/employee" in path and "/search" in path:
        if not rate_limit_search(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many search requests. Maximum 100 per minute."
            )
    else:
        if not rate_limit_default(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Maximum 60 per minute."
            )
    
    response = await call_next(request)
    
    # Agregar headers de rate limiting
    response.headers["X-RateLimit-Limit"] = DEFAULT_LIMITS.get("default", "60/minute")
    response.headers["X-RateLimit-Remaining"] = "59"  # Simplificado
    
    return response

# Funciones de monitoreo
def get_rate_limit_stats() -> dict:
    """Obtener estadísticas de rate limiting"""
    stats = {
        "total_keys": len(memory_limiter.requests),
        "active_requests": 0,
        "endpoint_breakdown": {}
    }
    
    now = time.time()
    
    for key, requests in memory_limiter.requests.items():
        # Contar requests activos (último minuto)
        active = sum(1 for req_time in requests if now - req_time < 60)
        stats["active_requests"] += active
        
        # Breakdown por endpoint
        parts = key.split(":")
        if len(parts) >= 2:
            endpoint = parts[1]
            if endpoint not in stats["endpoint_breakdown"]:
                stats["endpoint_breakdown"][endpoint] = 0
            stats["endpoint_breakdown"][endpoint] += active
    
    return stats

def clear_rate_limits():
    """Limpia todos los rate limits (para testing)"""
    memory_limiter.requests.clear()
    print("🧹 Rate limits cleared")

if __name__ == "__main__":
    # Testing
    print("🧪 Testing Rate Limiter")
    
    class MockRequest:
        def __init__(self, client_ip="127.0.0.1"):
            self.client = MockClient(client_ip)
            self.url = MockUrl("/api/upload")
    
    class MockClient:
        def __init__(self, host):
            self.host = host
    
    class MockUrl:
        def __init__(self, path):
            self.path = path
    
    # Test upload limit (10 por minuto)
    req = MockRequest()
    count = 0
    for i in range(15):
        if rate_limit_upload(req):
            count += 1
        else:
            break
    
    print(f"✅ Upload limit test: {count}/10 requests permitidos")
    
    # Mostrar estadísticas
    stats = get_rate_limit_stats()
    print(f"📊 Stats: {json.dumps(stats, indent=2)}")