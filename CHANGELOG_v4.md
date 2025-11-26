# 📋 ChinginGenerator v4 PRO - Changelog y Documentación

## 📅 Fecha: 25 de Noviembre, 2025

---

## 🆕 Nuevas Funcionalidades Implementadas

### 1. 📄 Módulo 賃金台帳 (Chingin Print)

#### Descripción
Nueva pestaña que permite buscar empleados por ID y generar la 賃金台帳 en formato Excel idéntico a la hoja "Print" del archivo `賃金台帳XP.xlsm`.

#### Características:
- **Búsqueda por ID de empleado**: Campo de búsqueda rápida
- **Selector de año**: Dropdown para elegir el año fiscal
- **Vista previa de datos**: Tabla con resumen mensual antes de descargar
- **Descarga Excel**: Genera archivo `.xlsx` con formato profesional

#### Endpoints API:
```
GET  /api/employee/{id}           → Buscar empleado por ID
GET  /api/employee/{id}/preview   → Vista previa de datos por año
GET  /api/employee/{id}/chingin   → Descargar 賃金台帳 Excel
```

#### Estructura del archivo generado (79 filas):
| Fila | Campo | Descripción |
|------|-------|-------------|
| 6 | 月 | Encabezado de meses (1-12) + 合計 |
| 7 | 支給年月日 | Fecha de pago |
| 8 | 賃金計算期間 | Periodo de cálculo |
| 9-12 | 勤怠 | Días/horas trabajadas |
| 13-17 | 時間 | Horas extras, nocturnas, festivos |
| 18-38 | 手当 | Subsidios y allowances |
| 39 | 非課税通勤費 | Transporte no gravable |
| 40-42 | 残業手当 | Horas extras |
| 63-65 | 支給合計 | Totales de pago |
| 66-76 | 控除 | Deducciones |
| 77-79 | 年末調整 | Ajuste de fin de año |

---

### 2. 🧮 Campos Calculados Especiales

#### その他手当１ (Fila 28)
- **Cálculo**: Suma de columnas X(1) a AE(8) del archivo original
- **Índices**: 23-30 (0-based)
- **Exclusión**: Se excluye automáticamente `通勤手当(非)` si está en este rango

#### その他 (Fila 76)
- **Cálculo**: Suma de columnas AN(控除1) a AU(控除8)
- **Índices**: 39-46 (0-based)

#### 年調過不足 (Filas 77-79)
- **Fuente**: Columna AV (控除9), índice 47
- **Lógica**:
  - Si valor < 0 → Mostrar en fila 78 (年末調整還付) como positivo
  - Si valor > 0 → Mostrar en fila 79 (年末調整徴収)

---

### 3. 📍 Detección Dinámica de Columnas

#### Problema resuelto:
La columna `通勤手当(非)` puede cambiar de posición en diferentes archivos Excel.

#### Solución implementada:
```python
# Buscar dinámicamente por nombre en headers
for idx, h in enumerate(headers):
    if h and '通勤' in str(h) and '非' in str(h):
        commuting_idx = idx
        break

# Guardar con cada registro
full_record = {
    "row_data": row_data,
    "headers": headers,
    "commuting_idx": commuting_idx  # Índice dinámico
}
```

#### En la suma de その他手当１:
```python
for idx in indices:
    # Excluir si este índice es el de 通勤手当(非)
    if commuting_idx is not None and idx == commuting_idx:
        continue
    # ... sumar valor
```

---

### 4. 🗑️ Función Borrar Todos los Datos

#### Ubicación:
- Botón en pestaña "Subir" 
- Botón en pestaña "Datos"

#### Características:
- **Doble confirmación** para evitar borrados accidentales
- **Backup automático** antes de borrar
- Elimina: empleados, registros de nómina, archivos procesados
- Muestra resumen de registros eliminados

#### Endpoint:
```
POST /api/clear-all
```

#### Respuesta:
```json
{
    "status": "success",
    "payroll_deleted": 150,
    "employees_deleted": 25,
    "backup_created": "backup_auto_20251125.db"
}
```

---

### 5. 📊 Barra de Progreso Detallada

#### Problema original:
La barra saltaba de 30% directamente al final sin mostrar progreso intermedio.

#### Solución:
Implementación de progreso simulado con `setInterval` que se actualiza cada 150ms.

#### Fases del progreso:

| Porcentaje | Icono | Mensaje |
|------------|-------|---------|
| 0-2% | 🚀 | Iniciando... |
| 2-5% | 📤 | Preparando envío... |
| 5-15% | 📤 | Enviando archivos... |
| 15-30% | 📂 | Archivos recibidos... |
| 30-45% | ⚙️ | Leyendo hojas Excel... |
| 45-60% | 📊 | Procesando registros... |
| 60-72% | 💾 | Guardando en base de datos... |
| 72-80% | 🔄 | Finalizando... |
| 80-100% | ✅ | Resultados por archivo |

#### Características adicionales:
- **Log en tiempo real** tipo terminal (fondo oscuro, texto verde)
- **Colores por tipo**: info=azul, success=verde, error=rojo
- **Progreso no lineal**: más lento cerca del final para parecer más natural
- **Tamaño adaptativo**: archivos grandes = progreso más lento

#### Código clave:
```javascript
// Reset inicial
progressBar.style.width = '0%';
progressPercent.textContent = '0%';

// Intervalo de actualización
progressInterval = setInterval(() => {
    const remaining = 80 - currentProgress;
    const increment = Math.max(0.3, Math.min(incrementPerTick, remaining * 0.08));
    currentProgress = Math.min(80, currentProgress + increment);
    // Actualizar UI...
}, 150);
```

---

## 📁 Archivos Modificados

### excel_processor.py
- **Líneas ~150-180**: Detección dinámica de `commuting_idx`
- **Líneas ~640**: Guardar `commuting_idx` en `by_month`
- **Líneas ~875-895**: Exclusión de transporte en suma de `その他手当１`
- **Función `generate_chingin_print()`**: Líneas 604-989

### app.py
- **Líneas ~156-225**: Endpoints para búsqueda de empleado
- **Líneas ~320-340**: Endpoint `/api/clear-all`

### database.py
- **Función `clear_all_data()`**: Líneas 410-435

### templates/index.html
- **Pestaña 賃金台帳**: Líneas ~250-400
- **Barra de progreso**: Líneas ~90-110
- **Función `handleFiles()`**: Líneas ~413-580
- **Función `clearAllData()`**: Líneas ~585-620

---

## 🗄️ Estructura de Base de Datos

### Tabla: employees
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    employee_id TEXT UNIQUE,
    name_roman TEXT,
    name_jp TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Tabla: payroll_records
```sql
CREATE TABLE payroll_records (
    id INTEGER PRIMARY KEY,
    employee_id TEXT,
    period TEXT,
    period_start DATE,
    period_end DATE,
    work_days REAL,
    work_hours REAL,
    overtime_hours REAL,
    base_pay REAL,
    total_pay REAL,
    deduction_total REAL,
    net_pay REAL,
    -- ... más campos
    created_at TIMESTAMP
)
```

---

## 🔧 Configuración Técnica

### Puerto del servidor
```
http://localhost:8989
```

### Dependencias principales
```
fastapi
uvicorn
openpyxl
sqlite3 (built-in)
```

### Iniciar servidor
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8989
```

---

## 📝 Notas Importantes

1. **Backups automáticos**: Se crean antes de borrar datos y cada cierto número de operaciones

2. **WAL mode**: SQLite usa Write-Ahead Logging para mejor concurrencia

3. **Timeout**: Conexiones DB tienen 30 segundos de timeout

4. **Formatos soportados**: `.xlsm`, `.xlsx`, `.xls`

5. **Hoja prioritaria**: El sistema busca hojas con nombres como "totalChin", "2025年", "総合", "ALL"

---

## 🐛 Problemas Conocidos y Soluciones

### Error: "通勤手当(非) en posición diferente"
**Solución**: Implementada detección dinámica por nombre de columna.

### Error: "Barra de progreso salta de 30% al final"
**Solución**: Implementado `setInterval` con progreso simulado continuo.

### Error: "NameError: OUTPUT_DIR not defined"
**Solución**: Se calcula dinámicamente la ruta del output.

---

## 📈 Próximas Mejoras Sugeridas

1. [ ] Exportación a PDF de la 賃金台帳
2. [ ] Filtros avanzados en tabla de datos
3. [ ] Gráficos de tendencias salariales
4. [ ] Notificaciones por email
5. [ ] Multi-idioma (日本語/Español/English)

---

*Documentación generada el 25 de Noviembre, 2025*
*ChinginGenerator v4 PRO - Sistema de Nóminas Japonesas*
