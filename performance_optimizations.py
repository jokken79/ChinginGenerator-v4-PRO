#!/usr/bin/env python3
"""
Optimizaciones de Performance para 賃金台帳 Generator v4 PRO
Implementa cache, bulk operations y optimizaciones de queries
"""

from functools import lru_cache, wraps
from typing import List, Dict, Any, Optional
import time
import sqlite3
import json
import os
from datetime import datetime, timedelta
import threading
from collections import defaultdict

# Configuración
CACHE_TTL = 300  # 5 minutos
BULK_BATCH_SIZE = 1000
ENABLE_QUERY_LOGGING = True

class PerformanceCache:
    """Cache con TTL y thread-safe"""
    
    def __init__(self, ttl_seconds: int = CACHE_TTL):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]["value"], self.cache[key]["timestamp"]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Guardar valor en cache"""
        with self.lock:
            self.cache[key] = {
                "value": value,
                "timestamp": time.time()
            }
    
    def clear(self) -> None:
        """Limpiar todo el cache"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Tamaño actual del cache"""
        with self.lock:
            return len(self.cache)

# Instancias globales
employee_cache = PerformanceCache(ttl=600)  # 10 minutos para empleados
company_cache = PerformanceCache(ttl=1800)  # 30 minutos para compañías
stats_cache = PerformanceCache(ttl=60)  # 1 minuto para estadísticas

def timed_cache(ttl_seconds: int = CACHE_TTL):
    """Decorador para caché con logging de tiempo"""
    def decorator(func):
        cache = PerformanceCache(ttl_seconds)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar key de cache
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Intentar obtener del cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"📦 CACHE HIT: {func.__name__}")
                return cached_result
            
            # Ejecutar función
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Guardar en cache
            cache.set(cache_key, result)
            
            if ENABLE_QUERY_LOGGING and duration > 0.1:
                print(f"⏱️ SLOW QUERY: {func.__name__} took {duration:.3f}s")
            
            return result
        
        # Agregar método clear al wrapper
        wrapper.cache_clear = cache.clear
        wrapper.cache_size = cache.size
        
        return wrapper
    return decorator

def bulk_insert_payroll_records(records: List[Dict[str, Any]]) -> int:
    """
    Insert masivo de registros de nómina con transaction
    Mucho más eficiente que insert individual
    """
    if not records:
        return 0
    
    start_time = time.time()
    
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            cursor = conn.cursor()
            
            # Preparar statement SQL
            sql = '''
                INSERT OR REPLACE INTO payroll_records (
                    source_file, employee_id, name_roman, name_jp, period,
                    period_start, period_end, work_days, work_hours, overtime_hours,
                    holiday_hours, night_hours, hourly_rate, base_pay, overtime_pay,
                    night_pay, holiday_pay, commuting_allowance, total_pay,
                    health_insurance, pension, employment_insurance, income_tax,
                    resident_tax, deduction_total, net_pay, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            # Preparar datos en lotes
            batch_data = []
            for record in records:
                batch_data.append((
                    record.get('source_file'),
                    record.get('employee_id'),
                    record.get('name_roman'),
                    record.get('name_jp'),
                    record.get('period'),
                    record.get('period_start'),
                    record.get('period_end'),
                    record.get('work_days', 0),
                    record.get('work_hours', 0),
                    record.get('overtime_hours', 0),
                    record.get('holiday_hours', 0),
                    record.get('night_hours', 0),
                    record.get('hourly_rate', 0),
                    record.get('base_pay', 0),
                    record.get('overtime_pay', 0),
                    record.get('night_pay', 0),
                    record.get('holiday_pay', 0),
                    record.get('commuting_allowance', 0),
                    record.get('total_pay', 0),
                    record.get('health_insurance', 0),
                    record.get('pension', 0),
                    record.get('employment_insurance', 0),
                    record.get('income_tax', 0),
                    record.get('resident_tax', 0),
                    record.get('deduction_total', 0),
                    record.get('net_pay', 0),
                    json.dumps(record, ensure_ascii=False, default=str)
                ))
            
            # Ejecutar insert masivo
            cursor.executemany(sql, batch_data)
            conn.commit()
            
            inserted_count = len(records)
            duration = time.time() - start_time
            
            print(f"📊 BULK INSERT: {inserted_count} records in {duration:.3f}s")
            
            return inserted_count
            
    except Exception as e:
        print(f"❌ BULK INSERT ERROR: {e}")
        return 0

@timed_cache(ttl_seconds=600)
def get_all_employees_cached() -> List[Dict[str, Any]]:
    """
    Obtener todos los empleados con cache
    Evita repetir queries frecuentes
    """
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.*, 
                       COUNT(pr.id) as payroll_count,
                       MAX(pr.period) as last_period
                FROM employees e
                LEFT JOIN payroll_records pr ON e.employee_id = pr.employee_id
                GROUP BY e.employee_id
                ORDER BY e.name_jp, e.name_roman
            ''')
            
            employees = [dict(row) for row in cursor.fetchall()]
            return employees
            
    except Exception as e:
        print(f"❌ get_all_employees_cached ERROR: {e}")
        return []

@timed_cache(ttl_seconds=1800)
def get_dispatch_companies_cached() -> List[Dict[str, Any]]:
    """
    Obtener compañías de despacho con cache
    Usado frecuentemente en UI
    """
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    he.dispatch_company,
                    COUNT(DISTINCT he.employee_id) as employee_count,
                    COUNT(DISTINCT pr.employee_id) as payroll_count
                FROM haken_employees he
                LEFT JOIN payroll_records pr ON he.employee_id = pr.employee_id
                WHERE he.dispatch_company IS NOT NULL 
                AND he.dispatch_company != ''
                GROUP BY he.dispatch_company
                ORDER BY he.dispatch_company
            ''')
            
            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'name': row['dispatch_company'],
                    'count': row['employee_count'],
                    'payroll_count': row['payroll_count'] or 0
                })
            
            return companies
            
    except Exception as e:
        print(f"❌ get_dispatch_companies_cached ERROR: {e}")
        return []

@timed_cache(ttl_seconds=60)
def get_statistics_cached() -> Dict[str, Any]:
    """
    Obtener estadísticas con cache de 1 minuto
    Evita recálculo constante
    """
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            cursor = conn.cursor()
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM payroll_records")
            total_records = cursor.fetchone()[0]
            
            # Contar empleados únicos
            cursor.execute("SELECT COUNT(DISTINCT employee_id) FROM payroll_records")
            unique_employees = cursor.fetchone()[0]
            
            # Contar períodos únicos
            cursor.execute("SELECT COUNT(DISTINCT period) FROM payroll_records")
            total_periods = cursor.fetchone()[0]
            
            # Sumar net pay
            cursor.execute("SELECT SUM(CAST(net_pay AS REAL)) FROM payroll_records")
            total_net_pay = cursor.fetchone()[0] or 0
            
            # Obtener hash de BD
            cursor.execute("SELECT hash FROM backups WHERE is_valid = 1 ORDER BY created_at DESC LIMIT 1")
            db_hash = cursor.fetchone()
            db_hash = db_hash[0] if db_hash else ""
            
            stats = {
                'total_payroll_records': total_records,
                'total_employees': unique_employees,
                'total_periods': total_periods,
                'total_net_pay': total_net_pay,
                'db_hash': db_hash,
                'cache_timestamp': datetime.now().isoformat()
            }
            
            return stats
            
    except Exception as e:
        print(f"❌ get_statistics_cached ERROR: {e}")
        return {}

def optimize_database_indexes():
    """
    Crear índices optimizados para performance
    Ejecutar una vez después de crear la BD
    """
    indexes = [
        # Índices compuestos para queries comunes
        "CREATE INDEX IF NOT EXISTS idx_payroll_emp_period ON payroll_records(employee_id, period)",
        "CREATE INDEX IF NOT EXISTS idx_payroll_period_emp ON payroll_records(period, employee_id)",
        
        # Índices para búsquedas de empleados
        "CREATE INDEX IF NOT EXISTS idx_employees_name_jp ON employees(name_jp)",
        "CREATE INDEX IF NOT EXISTS idx_employees_name_roman ON employees(name_roman)",
        "CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status)",
        
        # Índices para haken/ukeoi
        "CREATE INDEX IF NOT EXISTS idx_haken_dispatch ON haken_employees(dispatch_company)",
        "CREATE INDEX IF NOT EXISTS idx_haken_status ON haken_employees(status)",
        "CREATE INDEX IF NOT EXISTS idx_ukeoi_jobtype ON ukeoi_employees(job_type)",
        "CREATE INDEX IF NOT EXISTS idx_ukeoi_status ON ukeoi_employees(status)",
        
        # Índices para auditoría
        "CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)",
        
        # Índices para backups
        "CREATE INDEX IF NOT EXISTS idx_backups_created_at ON backups(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_backups_is_valid ON backups(is_valid)"
    ]
    
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            cursor = conn.cursor()
            
            for index_sql in indexes:
                cursor.execute(index_sql)
                print(f"✅ Index created/verified: {index_sql.split('idx_')[1].split(' ')[0]}")
            
            conn.commit()
            print("🚀 Database optimization completed")
            
    except Exception as e:
        print(f"❌ Database optimization ERROR: {e}")

def get_performance_metrics() -> Dict[str, Any]:
    """Obtener métricas de performance del sistema"""
    return {
        'cache_stats': {
            'employees_cache_size': employee_cache.size(),
            'company_cache_size': company_cache.size(),
            'stats_cache_size': stats_cache.size()
        },
        'database_info': get_database_info(),
        'system_info': {
            'python_version': os.sys.version,
            'platform': os.name
        }
    }

def get_database_info() -> Dict[str, Any]:
    """Obtener información de la base de datos"""
    try:
        with sqlite3.connect('chingin_data.db') as conn:
            cursor = conn.cursor()
            
            # Tamaño de la BD
            db_size = os.path.getsize('chingin_data.db')
            
            # Contar registros por tabla
            table_counts = {}
            tables = ['employees', 'payroll_records', 'haken_employees', 'ukeoi_employees', 'audit_log', 'backups']
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except:
                    table_counts[table] = 0
            
            return {
                'size_bytes': db_size,
                'size_mb': round(db_size / (1024 * 1024), 2),
                'table_counts': table_counts,
                'journal_mode': get_pragma(conn, 'journal_mode'),
                'cache_size': get_pragma(conn, 'cache_size')
            }
            
    except Exception as e:
        print(f"❌ get_database_info ERROR: {e}")
        return {}

def get_pragma(conn, pragma_name):
    """Obtener valor de pragma SQLite"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA {pragma_name}")
        return cursor.fetchone()[0]
    except:
        return None

def clear_all_caches():
    """Limpiar todos los caches"""
    employee_cache.clear()
    company_cache.clear()
    stats_cache.clear()
    print("🧹 All caches cleared")

if __name__ == "__main__":
    print("🚀 Performance Optimization Module")
    
    # Optimizar base de datos
    print("\n📊 Optimizing database indexes...")
    optimize_database_indexes()
    
    # Test cache functions
    print("\n🧪 Testing cache functions...")
    
    # Test empleados cache
    employees = get_all_employees_cached()
    print(f"✅ Employees cached: {len(employees)}")
    
    # Test estadísticas cache
    stats = get_statistics_cached()
    print(f"✅ Stats cached: {json.dumps(stats, indent=2)}")
    
    # Test métricas
    metrics = get_performance_metrics()
    print(f"✅ Performance metrics: {json.dumps(metrics, indent=2)}")
    
    print("\n🎉 Performance optimization complete!")