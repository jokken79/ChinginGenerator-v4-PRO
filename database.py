#!/usr/bin/env python3
"""
賃金台帳 Generator v4 PRO - Database Module
Base de datos SQLite para persistencia, auditoría y backups
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chingin_data.db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")


def get_db_path():
    return DB_PATH


@contextmanager
def get_connection():
    """Context manager para conexiones a la base de datos"""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Habilitar WAL mode para mejor concurrencia
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Inicializa la base de datos con todas las tablas"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # ========================================
        # TABLA: employees (従業員)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name_roman TEXT,
                name_jp TEXT,
                hourly_rate REAL,
                department TEXT,
                position TEXT,
                hire_date TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========================================
        # TABLA: payroll_records (賃金記録)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                period TEXT NOT NULL,
                period_start TEXT,
                period_end TEXT,
                work_days INTEGER DEFAULT 0,
                work_hours REAL DEFAULT 0,
                overtime_hours REAL DEFAULT 0,
                night_hours REAL DEFAULT 0,
                holiday_hours REAL DEFAULT 0,
                base_pay REAL DEFAULT 0,
                overtime_pay REAL DEFAULT 0,
                night_pay REAL DEFAULT 0,
                holiday_pay REAL DEFAULT 0,
                total_pay REAL DEFAULT 0,
                health_insurance REAL DEFAULT 0,
                pension REAL DEFAULT 0,
                employment_insurance REAL DEFAULT 0,
                income_tax REAL DEFAULT 0,
                resident_tax REAL DEFAULT 0,
                deduction_total REAL DEFAULT 0,
                net_pay REAL DEFAULT 0,
                source_file TEXT,
                raw_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, period),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)
        
        # ========================================
        # TABLA: audit_log (監査ログ)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_value TEXT,
                new_value TEXT,
                user_info TEXT,
                ip_address TEXT,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========================================
        # TABLA: backups (バックアップ)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER,
                backup_type TEXT DEFAULT 'auto',
                description TEXT,
                is_valid INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========================================
        # TABLA: processed_files (処理済みファイル)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT,
                file_hash TEXT,
                file_size INTEGER,
                records_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'success',
                error_message TEXT,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========================================
        # TABLA: settings (設定)
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar configuraciones por defecto
        default_settings = [
            ('auto_backup_enabled', 'true', 'Habilitar backup automático'),
            ('auto_backup_interval_hours', '24', 'Intervalo de backup en horas'),
            ('max_backups_keep', '30', 'Número máximo de backups a mantener'),
            ('integrity_check_enabled', 'true', 'Verificar integridad SHA256'),
            ('audit_log_enabled', 'true', 'Habilitar log de auditoría'),
        ]
        
        for key, value, desc in default_settings:
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, desc))
        
        # Crear índices para mejor rendimiento
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payroll_employee ON payroll_records(employee_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payroll_period ON payroll_records(period)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_date ON audit_log(created_at)")
        
        conn.commit()
        print("✓ Base de datos inicializada correctamente")


# ========================================
# FUNCIONES DE EMPLEADOS
# ========================================

def upsert_employee(employee_data: Dict) -> int:
    """Insertar o actualizar empleado"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO employees (employee_id, name_roman, name_jp, hourly_rate)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(employee_id) DO UPDATE SET
                name_roman = excluded.name_roman,
                name_jp = excluded.name_jp,
                hourly_rate = COALESCE(excluded.hourly_rate, hourly_rate),
                updated_at = CURRENT_TIMESTAMP
        """, (
            employee_data.get('employee_id'),
            employee_data.get('name_roman'),
            employee_data.get('name_jp'),
            employee_data.get('hourly_rate')
        ))
        
        return cursor.lastrowid


def get_all_employees() -> List[Dict]:
    """Obtener todos los empleados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE status = 'active' ORDER BY employee_id")
        return [dict(row) for row in cursor.fetchall()]


def get_employee(employee_id: str) -> Optional[Dict]:
    """Obtener empleado por ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


# ========================================
# FUNCIONES DE NÓMINA
# ========================================

def save_payroll_record(record: Dict) -> int:
    """Guardar registro de nómina"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Primero asegurar que el empleado existe (inline para evitar bloqueo)
        cursor.execute("""
            INSERT INTO employees (employee_id, name_roman, name_jp, hourly_rate)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(employee_id) DO UPDATE SET
                name_roman = COALESCE(excluded.name_roman, employees.name_roman),
                name_jp = COALESCE(excluded.name_jp, employees.name_jp),
                hourly_rate = COALESCE(excluded.hourly_rate, employees.hourly_rate),
                updated_at = CURRENT_TIMESTAMP
        """, (
            record.get('employee_id'),
            record.get('name_roman'),
            record.get('name_jp'),
            record.get('hourly_rate')
        ))
        
        cursor.execute("""
            INSERT INTO payroll_records (
                employee_id, period, period_start, period_end,
                work_days, work_hours, overtime_hours, night_hours, holiday_hours,
                base_pay, overtime_pay, night_pay, holiday_pay, total_pay,
                health_insurance, pension, employment_insurance,
                income_tax, resident_tax, deduction_total, net_pay,
                source_file, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, period) DO UPDATE SET
                work_days = excluded.work_days,
                work_hours = excluded.work_hours,
                overtime_hours = excluded.overtime_hours,
                night_hours = excluded.night_hours,
                holiday_hours = excluded.holiday_hours,
                base_pay = excluded.base_pay,
                overtime_pay = excluded.overtime_pay,
                night_pay = excluded.night_pay,
                holiday_pay = excluded.holiday_pay,
                total_pay = excluded.total_pay,
                health_insurance = excluded.health_insurance,
                pension = excluded.pension,
                employment_insurance = excluded.employment_insurance,
                income_tax = excluded.income_tax,
                resident_tax = excluded.resident_tax,
                deduction_total = excluded.deduction_total,
                net_pay = excluded.net_pay,
                source_file = excluded.source_file,
                raw_data = excluded.raw_data,
                updated_at = CURRENT_TIMESTAMP
        """, (
            record.get('employee_id'),
            record.get('period'),
            record.get('period_start'),
            record.get('period_end'),
            record.get('work_days', 0),
            record.get('work_hours', 0),
            record.get('overtime_hours', 0),
            record.get('night_hours', 0),
            record.get('holiday_hours', 0),
            record.get('base_pay', 0),
            record.get('overtime_pay', 0),
            record.get('night_pay', 0),
            record.get('holiday_pay', 0),
            record.get('total_pay', 0),
            record.get('health_insurance', 0),
            record.get('pension', 0),
            record.get('employment_insurance', 0),
            record.get('income_tax', 0),
            record.get('resident_tax', 0),
            record.get('deduction_total', 0),
            record.get('net_pay', 0),
            record.get('source_file'),
            json.dumps(record, ensure_ascii=False, default=str)
        ))
        
        # Log de auditoría (inline para evitar bloqueo)
        cursor.execute("""
            INSERT INTO audit_log (action, table_name, record_id, old_value, new_value, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('INSERT_PAYROLL', 'payroll_records', record.get('employee_id'), 
              None, json.dumps(record, ensure_ascii=False, default=str), None))
        
        return cursor.lastrowid


def get_payroll_by_employee(employee_id: str) -> List[Dict]:
    """Obtener nóminas de un empleado"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM payroll_records 
            WHERE employee_id = ? 
            ORDER BY period DESC
        """, (employee_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_payroll_by_period(period: str) -> List[Dict]:
    """Obtener nóminas de un periodo"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.*, e.name_roman, e.name_jp
            FROM payroll_records pr
            LEFT JOIN employees e ON pr.employee_id = e.employee_id
            WHERE pr.period = ?
            ORDER BY pr.employee_id
        """, (period,))
        return [dict(row) for row in cursor.fetchall()]


def get_all_payroll_records() -> List[Dict]:
    """Obtener todos los registros de nómina"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr.*, e.name_roman, e.name_jp
            FROM payroll_records pr
            LEFT JOIN employees e ON pr.employee_id = e.employee_id
            ORDER BY pr.period DESC, pr.employee_id
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_periods() -> List[str]:
    """Obtener lista de periodos únicos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT period FROM payroll_records ORDER BY period DESC")
        return [row[0] for row in cursor.fetchall()]


# ========================================
# FUNCIONES DE AUDITORÍA
# ========================================

def log_audit(action: str, table_name: str = None, record_id: str = None,
              old_value: str = None, new_value: str = None, details: str = None):
    """Registrar acción en log de auditoría"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (action, table_name, record_id, old_value, new_value, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (action, table_name, record_id, old_value, new_value, details))


def get_audit_log(limit: int = 100, action_filter: str = None) -> List[Dict]:
    """Obtener log de auditoría"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if action_filter:
            cursor.execute("""
                SELECT * FROM audit_log 
                WHERE action LIKE ? 
                ORDER BY created_at DESC LIMIT ?
            """, (f"%{action_filter}%", limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_log 
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]


def clear_all_data():
    """Borrar TODOS los datos de la base de datos (excepto backups y configuración)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Contar registros antes de borrar
        cursor.execute("SELECT COUNT(*) FROM payroll_records")
        payroll_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM employees")
        employee_count = cursor.fetchone()[0]
        
        # Borrar datos
        cursor.execute("DELETE FROM payroll_records")
        cursor.execute("DELETE FROM employees")
        cursor.execute("DELETE FROM processed_files")
        
        # Registrar en auditoría
        cursor.execute("""
            INSERT INTO audit_log (action, table_name, details)
            VALUES (?, ?, ?)
        """, ('CLEAR_ALL_DATA', 'all', f'Borrados {payroll_count} registros de nómina y {employee_count} empleados'))
        
        return {
            "payroll_deleted": payroll_count,
            "employees_deleted": employee_count,
            "status": "success"
        }


# ========================================
# FUNCIONES DE BACKUP E INTEGRIDAD
# ========================================

def calculate_file_hash(filepath: str) -> str:
    """Calcular hash SHA256 de un archivo"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def calculate_db_hash() -> str:
    """Calcular hash SHA256 de la base de datos"""
    return calculate_file_hash(DB_PATH)


def create_backup(backup_type: str = 'manual', description: str = None) -> Dict:
    """Crear backup de la base de datos"""
    import shutil
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"chingin_backup_{timestamp}.db"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copiar base de datos
    shutil.copy2(DB_PATH, backup_filepath)
    
    # Calcular hash
    file_hash = calculate_file_hash(backup_filepath)
    file_size = os.path.getsize(backup_filepath)
    
    # Registrar backup
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO backups (filename, filepath, file_hash, file_size, backup_type, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (backup_filename, backup_filepath, file_hash, file_size, backup_type, description))
    
    # Log de auditoría
    log_audit('CREATE_BACKUP', 'backups', backup_filename, None, None, 
              f"Hash: {file_hash}, Size: {file_size}")
    
    # Limpiar backups antiguos
    cleanup_old_backups()
    
    return {
        'filename': backup_filename,
        'filepath': backup_filepath,
        'hash': file_hash,
        'size': file_size,
        'created_at': timestamp
    }


def verify_backup_integrity(backup_id: int) -> Dict:
    """Verificar integridad de un backup"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backups WHERE id = ?", (backup_id,))
        backup = cursor.fetchone()
        
        if not backup:
            return {'valid': False, 'error': 'Backup no encontrado'}
        
        backup = dict(backup)
        
        if not os.path.exists(backup['filepath']):
            return {'valid': False, 'error': 'Archivo no existe'}
        
        current_hash = calculate_file_hash(backup['filepath'])
        is_valid = current_hash == backup['file_hash']
        
        # Actualizar estado
        cursor.execute("""
            UPDATE backups SET is_valid = ? WHERE id = ?
        """, (1 if is_valid else 0, backup_id))
        
        return {
            'valid': is_valid,
            'stored_hash': backup['file_hash'],
            'current_hash': current_hash,
            'filename': backup['filename']
        }


def restore_from_backup(backup_id: int) -> Dict:
    """Restaurar base de datos desde backup"""
    import shutil
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backups WHERE id = ?", (backup_id,))
        backup = cursor.fetchone()
        
        if not backup:
            return {'success': False, 'error': 'Backup no encontrado'}
        
        backup = dict(backup)
    
    # Verificar integridad primero
    integrity = verify_backup_integrity(backup_id)
    if not integrity['valid']:
        return {'success': False, 'error': f"Backup corrupto: {integrity.get('error', 'Hash no coincide')}"}
    
    # Crear backup del estado actual antes de restaurar
    current_backup = create_backup('pre_restore', 'Backup antes de restauración')
    
    # Restaurar
    try:
        shutil.copy2(backup['filepath'], DB_PATH)
        log_audit('RESTORE_BACKUP', 'backups', str(backup_id), None, None,
                  f"Restaurado desde: {backup['filename']}")
        
        return {
            'success': True,
            'restored_from': backup['filename'],
            'previous_backup': current_backup['filename']
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_backups() -> List[Dict]:
    """Obtener lista de backups"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backups ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def cleanup_old_backups():
    """Eliminar backups antiguos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Obtener configuración
        cursor.execute("SELECT value FROM settings WHERE key = 'max_backups_keep'")
        row = cursor.fetchone()
        max_keep = int(row[0]) if row else 30
        
        # Obtener backups a eliminar
        cursor.execute("""
            SELECT id, filepath FROM backups 
            ORDER BY created_at DESC
            LIMIT -1 OFFSET ?
        """, (max_keep,))
        
        old_backups = cursor.fetchall()
        
        for backup in old_backups:
            backup_id, filepath = backup
            if os.path.exists(filepath):
                os.remove(filepath)
            cursor.execute("DELETE FROM backups WHERE id = ?", (backup_id,))
        
        if old_backups:
            log_audit('CLEANUP_BACKUPS', 'backups', None, None, None,
                      f"Eliminados {len(old_backups)} backups antiguos")


def check_auto_backup():
    """Verificar si se necesita backup automático"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Verificar si está habilitado
        cursor.execute("SELECT value FROM settings WHERE key = 'auto_backup_enabled'")
        row = cursor.fetchone()
        if not row or row[0] != 'true':
            return None
        
        # Obtener intervalo
        cursor.execute("SELECT value FROM settings WHERE key = 'auto_backup_interval_hours'")
        row = cursor.fetchone()
        interval_hours = int(row[0]) if row else 24
        
        # Obtener último backup automático
        cursor.execute("""
            SELECT created_at FROM backups 
            WHERE backup_type = 'auto' 
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            # No hay backups, crear uno
            return create_backup('auto', 'Backup automático inicial')
        
        last_backup = datetime.fromisoformat(row[0].replace('Z', '+00:00') if 'Z' in row[0] else row[0])
        if datetime.now() - last_backup > timedelta(hours=interval_hours):
            return create_backup('auto', f'Backup automático ({interval_hours}h)')
        
        return None


# ========================================
# FUNCIONES DE CONFIGURACIÓN
# ========================================

def get_setting(key: str) -> Optional[str]:
    """Obtener configuración"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None


def set_setting(key: str, value: str, description: str = None):
    """Guardar configuración"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        """, (key, value, description))


def get_all_settings() -> Dict:
    """Obtener todas las configuraciones"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value, description FROM settings")
        return {row[0]: {'value': row[1], 'description': row[2]} for row in cursor.fetchall()}


# ========================================
# ESTADÍSTICAS
# ========================================

def get_statistics() -> Dict:
    """Obtener estadísticas generales"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total empleados
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
        stats['total_employees'] = cursor.fetchone()[0]
        
        # Total registros de nómina
        cursor.execute("SELECT COUNT(*) FROM payroll_records")
        stats['total_payroll_records'] = cursor.fetchone()[0]
        
        # Periodos únicos
        cursor.execute("SELECT COUNT(DISTINCT period) FROM payroll_records")
        stats['total_periods'] = cursor.fetchone()[0]
        
        # Totales
        cursor.execute("SELECT SUM(total_pay), SUM(net_pay) FROM payroll_records")
        row = cursor.fetchone()
        stats['total_gross_pay'] = row[0] or 0
        stats['total_net_pay'] = row[1] or 0
        
        # Archivos procesados
        cursor.execute("SELECT COUNT(*) FROM processed_files WHERE status = 'success'")
        stats['files_processed'] = cursor.fetchone()[0]
        
        # Backups
        cursor.execute("SELECT COUNT(*) FROM backups WHERE is_valid = 1")
        stats['valid_backups'] = cursor.fetchone()[0]
        
        # Último backup
        cursor.execute("SELECT created_at FROM backups ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        stats['last_backup'] = row[0] if row else None
        
        # Integridad de BD
        stats['db_hash'] = calculate_db_hash()
        
        return stats


# ========================================
# INICIALIZACIÓN
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("🗄️  Inicializando Base de Datos - ChinginApp v4 PRO")
    print("="*60)
    
    init_database()
    
    # Mostrar estadísticas
    stats = get_statistics()
    print(f"\n📊 Estadísticas:")
    print(f"   Empleados: {stats['total_employees']}")
    print(f"   Registros de nómina: {stats['total_payroll_records']}")
    print(f"   Periodos: {stats['total_periods']}")
    print(f"   Backups válidos: {stats['valid_backups']}")
    print(f"   Hash BD: {stats['db_hash'][:16]}...")
    
    print("\n✅ Base de datos lista!")
