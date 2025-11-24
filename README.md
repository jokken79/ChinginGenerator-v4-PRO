# 賃金台帳 Generator v4 PRO 📊

Sistema completo de procesamiento de nóminas japonesas con base de datos SQLite.

## ✨ Características PRO

| Función | Descripción |
|---------|-------------|
| 🗄️ **Base de Datos** | SQLite para persistencia de datos |
| 💾 **Auto-backup** | Backups automáticos cada 24 horas |
| 🔐 **Integridad SHA256** | Verificación de integridad de archivos |
| 📋 **Auditoría** | Log de todas las acciones |
| 🔄 **Restauración** | Restaurar desde cualquier backup |

## 🚀 Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar
python run.py

# 3. Abrir navegador en http://localhost:8989
```

## 📁 Estructura

```
ChinginApp_v4_PRO/
├── app.py              ← API FastAPI
├── database.py         ← Base de datos SQLite
├── excel_processor.py  ← Procesador de Excel
├── run.py              ← Launcher
├── requirements.txt    ← Dependencias
├── templates/
│   └── index.html      ← Interfaz web
├── uploads/            ← Archivos subidos
├── outputs/            ← Archivos generados
└── backups/            ← Backups de BD
```

## 📊 Base de Datos

### Tablas

| Tabla | Descripción |
|-------|-------------|
| `employees` | Datos de empleados |
| `payroll_records` | Registros de nómina |
| `audit_log` | Log de auditoría |
| `backups` | Control de respaldos |
| `processed_files` | Archivos procesados |
| `settings` | Configuraciones |

## 🔧 API Endpoints

### Datos
- `POST /api/upload` - Subir archivos Excel
- `GET /api/data` - Obtener todos los datos
- `GET /api/stats` - Estadísticas

### Exportación
- `GET /api/export/all` - Excel ALL consolidado
- `GET /api/export/monthly` - Excel por mes
- `GET /api/export/chingin` - 賃金台帳 ZIP

### Backup
- `POST /api/backup` - Crear backup
- `GET /api/backups` - Lista de backups
- `POST /api/backup/{id}/verify` - Verificar integridad
- `POST /api/backup/{id}/restore` - Restaurar

### Auditoría
- `GET /api/audit` - Log de auditoría

## 👨‍💻 Desarrollado por

Claude AI + K.Kaneshiro

**Versión:** 4.0.0 PRO  
**Fecha:** 2025
