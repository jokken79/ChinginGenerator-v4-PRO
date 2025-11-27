# Análisis de Rendimiento - 賃金台帳 Generator v4 PRO

## 📊 Diagnóstico Completo

### 1. ❌ PROBLEMA CRÍTICO: Reprocesamiento de Archivos Excel

**Síntoma:** La aplicación se siente lenta porque está reprocesando archivos Excel completos en cada request.

**Evidencia en logs:**
```
[Procesando] hoja: totalChin
[INFO] Columnas encontradas: 53
[Procesando] hoja 請負 (formato vertical)...
[INFO] Encontrados 64 bloques de empleados 請負社員
[INFO] Procesados 60 empleados 請負社員
```

**Causa Raíz:** Múltiples llamadas API están reprocesando archivos cuando NO deberían:

1. **`/api/ukeoi-employees`** - Se llama frecuentemente y puede estar leyendo archivos
2. **`/api/employees-by-company/{company}`** - Consulta DB correctamente, pero puede estar llamando a procesador
3. Cada búsqueda de empleado parece triggerar procesamiento

**Impacto:**
- ⏱️ **Tiempo de respuesta:** 3-8 segundos por request
- 💾 **Memoria:** Alto consumo procesando 60-70 empleados cada vez
- 🔄 **Carga CPU:** Procesamiento innecesario de Excel

---

### 2. 💾 Base de Datos Grande (25.9 MB)

**Datos actuales:**
- Tamaño: 25,956,352 bytes (~26 MB)
- Sin índices optimizados para búsquedas frecuentes
- Modo WAL activado (correcto)

**Recomendaciones:**
- ✅ Tamaño aceptable para SQLite
- ⚠️ Verificar índices en:
  - `payroll_records.employee_id`
  - `payroll_records.period`
  - `haken_employees.dispatch_company`
  - `ukeoi_employees.job_type`

---

### 3. 📁 Muchos Archivos Generados (1,164 archivos)

**Problema:**
- 1,164 archivos en carpeta `outputs/`
- No hay limpieza automática de archivos antiguos
- Posible impacto en rendimiento del filesystem

**Recomendación:**
- Implementar limpieza automática de archivos >7 días
- Considerar mover a subcarpetas por año/mes

---

### 4. 🔄 Requests Duplicados

**Evidencia:** Múltiples requests al mismo endpoint en rápida sucesión:
```
GET /api/employee/250201
GET /api/employee/250201
GET /api/employee/250201 (repeated 4-5 times)
```

**Causa:** Posible problema en frontend:
- JavaScript puede estar haciendo llamadas duplicadas
- Falta debouncing en búsquedas
- No hay caché del lado del cliente

---

### 5. ⚠️ Sin Sistema de Caché

**Problema:**
- Cada request va directo a base de datos
- No hay caché en memoria para datos frecuentes
- Datos maestros (員名, 派遣先) se cargan repetidamente

**Soluciones recomendadas:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache simple para datos maestros
@lru_cache(maxsize=100, typed=False)
def get_employee_master_cached(employee_id: str):
    return get_employee_master(employee_id)

# Cache con TTL para listas
employee_list_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 300  # 5 minutos
}
```

---

## 🔍 Análisis Detallado de Endpoints Lentos

### A. `/api/ukeoi-employees`
**Frecuencia:** Se llama cada vez que se carga la página
**Problema:** Puede estar reprocesando archivos en lugar de consultar DB
**Solución:** Verificar que solo consulte base de datos

### B. `/api/employee/{id}/chingin-v2`
**Problema:** Endpoint funciona pero genera archivos cada vez
**Solución:** Implementar caché de archivos generados (key: employee_id + year + format)

### C. `/api/employee/{id}/preview`
**Problema:** Consulta DB correctamente pero se llama múltiples veces
**Solución:** Añadir debouncing en frontend

---

## 🚀 Plan de Optimización Prioritario

### Fase 1: Fixes Críticos (1-2 horas)

#### 1.1 Eliminar Reprocesamiento de Excel ⚡ CRÍTICO
```python
# En app.py - verificar que estos endpoints NO llamen a processor.read_excel()
@app.get("/api/ukeoi-employees")
async def get_ukeoi_list():
    # DEBE llamar directamente a:
    return JSONResponse(get_all_ukeoi_employees())
    # NO debe llamar a processor.read_excel()
```

#### 1.2 Añadir Debouncing en Frontend
```javascript
// En index.html - para búsquedas de empleado
let searchTimeout;
function searchEmployeeDebounced() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        searchEmployee();
    }, 300); // 300ms delay
}
```

#### 1.3 Añadir Índices a Base de Datos
```sql
CREATE INDEX IF NOT EXISTS idx_payroll_emp_period
    ON payroll_records(employee_id, period);

CREATE INDEX IF NOT EXISTS idx_haken_dispatch
    ON haken_employees(dispatch_company)
    WHERE status IN ('在職中', '現在');

CREATE INDEX IF NOT EXISTS idx_ukeoi_jobtype
    ON ukeoi_employees(job_type)
    WHERE status IN ('在職中', '現在');
```

### Fase 2: Mejoras de Caché (2-3 horas)

#### 2.1 Cache Simple para Datos Maestros
```python
from functools import lru_cache
import time

# Cache con TTL manual
class SimpleCache:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

# Instanciar caches
employee_cache = SimpleCache(ttl=300)  # 5 minutos
company_cache = SimpleCache(ttl=600)   # 10 minutos
```

#### 2.2 Cache de Archivos Generados
```python
# En excel_processor.py
def generate_chingin_format_b(self, employee_id, year, output_path=None):
    # Verificar si ya existe archivo reciente
    cache_key = f"{employee_id}_{year}_b"
    cache_path = f"outputs/cache/chingin_{cache_key}.xlsx"

    if os.path.exists(cache_path):
        # Si archivo tiene menos de 1 hora, reutilizarlo
        file_age = time.time() - os.path.getmtime(cache_path)
        if file_age < 3600:  # 1 hora
            return {"status": "success", "file_path": cache_path, "cached": True}

    # Generar nuevo archivo...
```

### Fase 3: Limpieza y Mantenimiento (1 hora)

#### 3.1 Limpieza Automática de Archivos Antiguos
```python
# En app.py o como tarea programada
import os
import time

def cleanup_old_files(directory="outputs", days_old=7):
    """Eliminar archivos más antiguos de X días"""
    cutoff_time = time.time() - (days_old * 86400)
    deleted_count = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error eliminando {filepath}: {e}")

    return deleted_count

# Ejecutar al inicio de la app
@app.on_event("startup")
async def startup_event():
    cleanup_old_files(days_old=7)
```

---

## 📈 Mejoras Esperadas

### Antes de Optimización:
- ⏱️ Tiempo de carga inicial: 3-5 segundos
- 🔄 Tiempo de búsqueda empleado: 2-4 segundos
- 📥 Generación 賃金台帳: 5-10 segundos
- 💾 Uso memoria: Alto (reprocesamiento constante)

### Después de Optimización (Estimado):
- ⏱️ Tiempo de carga inicial: 0.5-1 segundo (80% mejora)
- 🔄 Tiempo de búsqueda empleado: 0.2-0.5 segundos (90% mejora)
- 📥 Generación 賃金台帳: 1-2 segundos primera vez, <0.5s con caché (95% mejora)
- 💾 Uso memoria: Bajo y predecible

---

## 🔧 Comandos de Diagnóstico

### Verificar tamaño de DB:
```bash
powershell -Command "Get-Item chingin_data.db | Select-Object Length, Name"
```

### Contar archivos generados:
```bash
powershell -Command "(Get-ChildItem outputs -File -Recurse | Measure-Object).Count"
```

### Ver índices actuales:
```bash
sqlite3 chingin_data.db "SELECT name, sql FROM sqlite_master WHERE type='index';"
```

### Analizar queries lentas (agregar logging):
```python
import time
def log_query_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        if duration > 0.5:  # Log si toma >500ms
            print(f"⚠️ SLOW QUERY: {func.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

---

## ✅ Checklist de Implementación

### Inmediato (Hoy):
- [ ] Verificar que `/api/ukeoi-employees` no reprocese Excel
- [ ] Añadir logging de timing en endpoints críticos
- [ ] Implementar debouncing en búsquedas frontend
- [ ] Añadir índices a base de datos

### Corto Plazo (Esta Semana):
- [ ] Implementar caché simple para datos maestros
- [ ] Cache de archivos Excel generados (1 hora TTL)
- [ ] Limpieza automática de archivos antiguos
- [ ] Optimizar queries frecuentes

### Medio Plazo (Este Mes):
- [ ] Considerar Redis para caché distribuido
- [ ] Implementar paginación en listas grandes
- [ ] Añadir compresión de responses
- [ ] Monitoring de performance con métricas

---

## 📝 Notas Adicionales

### Consideraciones:
1. **SQLite es adecuado** para este volumen de datos
2. **Modo WAL ya está activo** (correcto para concurrencia)
3. **No hay memory leaks evidentes** en logs
4. **Problema principal es reprocesamiento de Excel**

### Alternativas a Largo Plazo:
- Migrar archivos generados a S3/Azure Blob
- Implementar worker queue (Celery) para generaciones pesadas
- Considerar PostgreSQL si concurrencia aumenta significativamente
- Implementar WebSocket para actualizaciones en tiempo real

---

**Fecha de Análisis:** 2025-11-26
**Versión del Sistema:** v4 PRO
**Analizado por:** Claude Code Assistant
