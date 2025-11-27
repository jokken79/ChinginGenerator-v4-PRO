# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) cuando trabaja con código en este repositorio.

## Descripción del Proyecto

**賃金台帳 Generator v4 PRO** - Sistema de procesamiento de nóminas japonesas que genera libros de salarios (賃金台帳) a partir de datos de Excel. El sistema procesa archivos de recibos de sueldo japoneses (給与明細), los almacena en SQLite y genera diversos informes incluyendo libros de salarios individuales por empleado.

**Stack:** Python 3.11, FastAPI, SQLite, openpyxl, Uvicorn
**Idiomas:** Documentación y UI mezclada en español/japonés

## Comandos de Desarrollo Comunes

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación (abre navegador automáticamente)
python run.py

# Ejecutar con uvicorn directamente
python -m uvicorn app:app --host 0.0.0.0 --port 8989 --reload

# Inicializar/probar base de datos
python database.py

# Probar procesador de Excel
python excel_processor.py
```

### Despliegue con Docker
```bash
# Construir e iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f chingin-app

# Detener
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Acceder al shell del contenedor
docker exec -it chingin-generator-app bash
```

**URL:** http://localhost:8989

## Arquitectura General

### Arquitectura de Tres Capas

1. **Backend FastAPI (app.py)**
   - Endpoints API RESTful para todas las operaciones
   - Manejo de carga de archivos con multipart/form-data
   - Modelos de respuesta devuelven JSON o descargas de archivos
   - Al iniciar: inicializa base de datos y verifica auto-backup

2. **Capa de Procesamiento (excel_processor.py)**
   - Lee archivos Excel con datos de nómina japonesa
   - Parsea formato de 53 columnas de la hoja totalChin generada por macro VBA
   - Mantiene copia en memoria de todos los registros con datos completos de columnas
   - Guarda campos esenciales en base de datos para consultas
   - Genera varios formatos de exportación (ALL, por mes, 賃金台帳 individuales)

3. **Capa de Datos (database.py)**
   - SQLite con modo WAL para mejor concurrencia
   - Patrón context manager para manejo de conexiones
   - Sistema de backup automático con verificación de integridad SHA256
   - Logging de auditoría para todas las operaciones importantes

### Flujo de Datos Crítico

**Cargar → Procesar → Almacenar:**
1. Usuario sube archivo(s) Excel vía `/api/upload`
2. `ExcelProcessor` lee desde hojas prioritarias (totalChin, 2025年, ALL, etc.)
3. Valida employee_id (debe ser numérico, 6+ dígitos)
4. Almacena datos completos de fila en memoria (`all_records`) para exportaciones completas
5. Guarda campos esenciales en SQLite vía `save_payroll_record()`
6. Retorna éxito/error para cada archivo

**Sincronización de Maestro de Empleados:**
- Sincroniza desde carpeta de red: `//UNS-Kikaku/共有フォルダ/SCTDateBase/【新】社員台帳(UNS)T　2022.04.05～.xlsm`
- Nota: nombre de archivo contiene espacio de ancho completo (\u3000) entre T y 2022
- Dos tipos de empleados: 派遣社員 (haken_employees) y 請負社員 (ukeoi_employees)
- Endpoint: `/api/sync-employees` para ambos, o `/api/sync-haken`, `/api/sync-ukeoi` individualmente

**Generar 賃金台帳 (Libro de Salarios):**
- `/api/employee/{employee_id}/chingin?year=2025` genera Excel estilo Print
- Formato coincide con hoja Print de macro VBA: 80 filas cubriendo todos los ítems de pago/deducciones
- Muestra datos mensuales (1月～12月) más columna de totales
- Manejo especial:
  - Campos de tiempo en formato H:MM (work_hours, overtime_hours, night_hours)
  - その他手当１ = suma de subsidios [1-8] excluyendo 通勤手当(非)
  - その他 (deducciones) = suma de 控除1-8
  - 年末調整還付/徴収 dividido de 控除9 según positivo/negativo
  - Posición de 通勤手当(非) detectada dinámicamente por archivo

## Esquema de Base de Datos

### Tablas Principales

**employees** - Registro básico de empleados
- employee_id (UNIQUE) - 従業員番号
- name_roman, name_jp - Nombres del empleado
- hourly_rate, department, position, hire_date, status

**payroll_records** - Entradas de nómina mensuales
- UNIQUE(employee_id, period) - Previene entradas duplicadas por mes
- Rastrea días/horas trabajadas, horas extra, componentes de pago, deducciones
- raw_data JSON blob preserva registro original
- Foreign key a employees

**haken_employees** - Maestro 派遣社員 (sincronizado desde Excel de red)
- Contiene dispatch_company (派遣先), tarifas de facturación, info de visa
- 30 columnas incluyendo hourly_rate_history, profit_margin, etc.

**ukeoi_employees** - Maestro 請負社員 (sincronizado desde Excel de red)
- Contiene job_type (請負業務), info de viaje, seguro social
- Estructura similar a haken pero modelo de negocio diferente

**audit_log** - Todas las operaciones registradas
- action, table_name, record_id, old_value, new_value, details, created_at

**backups** - Metadata de respaldos
- filename, filepath, file_hash (SHA256), file_size, backup_type (auto/manual)
- Bandera is_valid actualizada después de verificaciones de integridad

**settings** - Configuración de aplicación (clave-valor)
- auto_backup_enabled, auto_backup_interval_hours, max_backups_keep
- integrity_check_enabled, audit_log_enabled

### Patrones Importantes

- Todas las tablas usan TEXT para fechas (formato ISO o formato japonés)
- Cláusulas ON CONFLICT para comportamiento de upsert
- Modo WAL (PRAGMA journal_mode=WAL) para lecturas concurrentes
- Foreign keys aplicadas en payroll_records → employees
- Índices en employee_id y period para rendimiento de consultas

## Lógica de Negocio Clave

### Mapeo de Columnas Excel (53 columnas, indexadas desde 0)

El sistema espera un formato específico de 53 columnas de la hoja totalChin de la macro VBA:
- Cols 0-5: Number, 従業員番号, 氏名ローマ字, 氏名, 支給分, 派遣先
- Cols 6-7: 賃金計算期間S/F (fechas inicio/fin)
- Cols 8-17: Métricas de trabajo (días, horas incluyendo horas extra/nocturnas con columnas de minutos separadas)
- Cols 18-22: Pago base y componentes de pago de horas extra
- Cols 23-30: Subsidios 1-8 (手当1～8)
- Col 31: 前月給与 (pago mes anterior)
- Col 32: 合計 (pago total)
- Cols 33-38: Seguro social e impuestos
- Cols 39-47: Deducciones 1-9 (控除1～9)
- Cols 48-49: 控除合計, 差引支給額 (deducción total, pago neto)
- Col 50: 通勤手当(非) - subsidio de viaje no gravable (posición puede variar - detectada dinámicamente)
- Cols 51-52: Otros subsidios/misceláneos

### Manejo de Formato de Periodo

Periodos vienen en formato: "2025年1月分(2月17日支給分)" (Enero 2025, pagado 17 de febrero)
- Extracción: Regex `r'(\d{4}年\d{1,2}月分)'` captura solo "2025年1月分"
- Este formato normalizado se usa para agrupar por mes en exportaciones

### Detección Dinámica de Columnas

La posición de columna 通勤手当(非) puede variar entre archivos. El procesador:
1. Escanea headers buscando palabras clave '通勤' y '非'
2. Almacena el índice detectado en metadata de cada registro
3. Usa este índice al generar 賃金台帳 para excluirlo de sumas de subsidios

### Sistema de Backup

Auto-backup se dispara cuando:
- `auto_backup_enabled = 'true'` en settings
- Tiempo desde último auto backup > `auto_backup_interval_hours`
- Default: 24 horas

Backups manuales pueden crearse vía endpoint `/api/backup`.

Todos los backups:
- Crean copia física de chingin_data.db
- Calculan hash SHA256 para integridad
- Almacenan metadata en tabla backups
- Limpieza mantiene solo `max_backups_keep` más recientes (default: 30)

Proceso de restauración:
1. Verifica integridad del backup (coincidencia SHA256)
2. Crea backup de seguridad de BD actual
3. Reemplaza BD actual con archivo de backup
4. Registra acción de restauración en audit_log

## Notas de Desarrollo

### Peculiaridades de Manejo de Fechas
- Números seriales de Excel (días desde 1899-12-30) se convierten en helper `format_date()`
- Base de datos almacena fechas como TEXT en formato ISO (YYYY-MM-DD)
- Formatos de visualización varían: formato japonés "YYYY年MM月DD日", formato con barras "YYYY/MM/DD", o ISO

### Consideraciones Multi-idioma
- Etiquetas de frontend: mezcla de japonés y español
- Respuestas API: nombres de campos en inglés
- Nombres de columnas de base de datos: inglés
- Mensajes de log: mezcla de español y japonés
- Headers de Excel: japonés

### Enfoque de Testing
- No hay suite de tests automatizados actualmente
- Testing manual vía archivos de test en raíz (test_month.py, test_process.py)
- Procesador Excel tiene bloque de test `if __name__ == "__main__"` con ruta de archivo hardcodeada
- Endpoint de health check: `/api/health` retorna estado, versión, hash BD, conteos de registros

### Patrón de Manejo de Errores
- Bloques try-except en procesador retornan `{"status": "error", "message": str(e)}`
- Operaciones de base de datos registran en audit_log en errores con sufijo de acción `_ERROR`
- FastAPI automáticamente retorna 500 para excepciones no manejadas
- No hay clases de excepción personalizadas definidas

## Flujos de Trabajo Comunes

### Agregar Nuevo Formato de Exportación
1. Agregar método a clase ExcelProcessor (seguir patrón de `export_to_excel_all()`)
2. Usar `self.all_records` para acceso completo de columnas o consultar base de datos con `get_all_payroll_records()`
3. Agregar endpoint correspondiente en app.py retornando FileResponse
4. Llamar `log_audit()` con nombre de acción
5. Actualizar frontend para agregar botón/enlace para nueva exportación

### Agregar Nuevo Endpoint API
1. Definir ruta en app.py con decorador apropiado (@app.get, @app.post)
2. Importar funciones necesarias de database.py o usar métodos de processor
3. Retornar JSONResponse o FileResponse
4. Para cargas de archivos, usar `List[UploadFile] = File(...)`
5. Agregar logging de auditoría si se modifican datos
6. Actualizar JavaScript de frontend para llamar nuevo endpoint

### Cambios de Esquema de Base de Datos
1. Modificar sentencias CREATE TABLE en función `init_database()`
2. Agregar índices si se consulta por nuevas columnas
3. Actualizar funciones afectadas de upsert/insert
4. Agregar lógica de migración o eliminar/recrear (no hay sistema formal de migración)
5. Probar con `python database.py`

### Actualizaciones de Despliegue
1. Hacer cambios de código
2. Actualizar versión en app.py (línea 44) y README.md
3. Commit de cambios
4. `docker-compose down`
5. `docker-compose up -d --build`
6. Verificar vía health check: `curl http://localhost:8989/api/health`

## Ubicaciones de Archivos Importantes

### Volúmenes Docker (Datos Persistentes)
- `/app/data/chingin_data.db` - Base de datos SQLite
- `/app/uploads/` - Archivos Excel subidos (temporales)
- `/app/outputs/` - Reportes generados
- `/app/backups/` - Archivos de backup de base de datos

### Desarrollo Local
- `d:\ChinginGenerator-v4-PRO\` - Raíz del proyecto
- `chingin_data.db` - Base de datos en raíz durante dev local
- `uploads/`, `outputs/`, `backups/` - Creados automáticamente

### Dependencias de Red
- Excel maestro de empleados: `//UNS-Kikaku/共有フォルダ/SCTDateBase/【新】社員台帳(UNS)T　2022.04.05～.xlsm`
  - Debe ser accesible desde ambiente de ejecución
  - Contiene hojas: DBGenzaiX (派遣), DBUkeoiX (請負)
  - Usado por endpoints `/api/sync-employees`

## Consideraciones de Seguridad

- **Sin autenticación/autorización** - Todos los endpoints API son públicos
- Base de datos usa SQLite, no diseñada para alta concurrencia
- Archivos subidos no se escanean por malware
- Sin sanitización de input en rutas de archivos
- Contenedor Docker ejecuta como usuario no-root `chingin` (buena práctica)
- Sin HTTPS/TLS - asume ambiente de red confiable
- SHA256 usado para integridad de backup, no para seguridad

## Notas de Rendimiento

- Modo WAL de SQLite permite lecturas concurrentes pero escritor único
- Dataset completo mantenido en memoria (`all_records`) para exportaciones - puede no escalar a datasets muy grandes
- Sin paginación en endpoints API - retorna todos los registros
- Generación de Excel es sincrónica - archivos grandes pueden timeout
- Sin capa de caché - cada request golpea base de datos o sistema de archivos

## Resolución de Problemas

**No se puede conectar a la base de datos:**
- Verificar permisos de archivo en chingin_data.db
- Verificar que ningún otro proceso tiene bloqueo exclusivo
- Buscar archivos .db-wal y .db-shm (artefactos de modo WAL)

**Falla procesamiento de Excel:**
- Verificar que archivo tiene hoja totalChin o nombrada por año (ej. 2025年)
- Revisar que conteo de columnas coincide con formato esperado de 53 columnas
- Confirmar que valores de employee_id son numéricos y de 6+ dígitos
- Buscar problemas de codificación japonesa en nombres de archivos

**Falla sincronización de maestro de empleados:**
- Verificar que carpeta de red es accesible: `//UNS-Kikaku/共有フォルダ/SCTDateBase/`
- Revisar que nombre de archivo coincide exactamente (nota espacio de ancho completo): `【新】社員台帳(UNS)T　2022.04.05～.xlsm`
- Asegurar que openpyxl puede abrir archivos .xlsm (puede necesitar habilitar macros)
- Verificar que hojas DBGenzaiX y DBUkeoiX existen en archivo maestro

**賃金台帳 generado falta datos:**
- Verificar si empleado tiene registros en base de datos: `/api/employee/{id}`
- Verificar que `all_records` está poblado (requiere procesar archivos en sesión actual)
- Confirmar parámetro de año correcto pasado
- Revisar que regex de extracción de mes coincide con formato de periodo
