@echo off
echo ========================================
echo 賃金台帳 Generator v4.1 PRO - Instalación de Optimizaciones
echo ========================================
echo.

echo [1/5] Instalando dependencias actualizadas...
pip install -r requirements_updated.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas correctamente
echo.

echo [2/5] Verificando módulos de optimización...
python -c "from performance_optimizations import PerformanceCache; print('✅ Módulo de optimizaciones funcionando')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Módulo de optimizaciones no disponible (usará funciones originales)
) else (
    echo ✅ Módulo de optimizaciones cargado
)

python -c "from claude_agents import PayrollAnalyzerAgent; print('✅ Agentes Claude funcionando')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Agentes Claude no disponibles (análisis avanzado desactivado)
) else (
    echo ✅ Agentes Claude cargados
)
echo.

echo [3/5] Optimizando base de datos...
python -c "
import sqlite3
conn = sqlite3.connect('chingin.db')
conn.execute('CREATE INDEX IF NOT EXISTS idx_payroll_employee_id ON payroll_records(employee_id)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_payroll_period ON payroll_records(period)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_employees_type ON employees(employee_type)')
conn.commit()
conn.close()
print('✅ Índices de base de datos creados')
"
if %errorlevel% neq 0 (
    echo ⚠️ Error optimizando base de datos
) else (
    echo ✅ Base de datos optimizada
)
echo.

echo [4/5] Limpiando archivos viejos...
python -c "
import os
import glob
from datetime import datetime, timedelta

cutoff_time = datetime.now() - timedelta(days=7)
deleted_count = 0

for pattern in ['uploads/*.xlsx', 'uploads/*.xlsm', 'uploads/*.xls']:
    for filepath in glob.glob(pattern):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff_time:
                os.remove(filepath)
                deleted_count += 1
        except:
            pass

print(f'🗑️ Eliminados {deleted_count} archivos viejos')
"
echo ✅ Limpieza completada
echo.

echo [5/5] Iniciando aplicación optimizada...
echo.
echo 🚀 Iniciando 賃金台帳 Generator v4.1 PRO OPTIMIZADO
echo 📊 URL: http://localhost:8989
echo 🔧 Health Check: http://localhost:8989/api/health
echo 📈 Cache Stats: http://localhost:8989/api/cache/stats
echo 🤖 Agentes Status: http://localhost:8989/api/agents/status
echo.
echo Presiona Ctrl+C para detener la aplicación
echo ========================================
echo.

python app.py
pause