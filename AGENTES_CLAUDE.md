# Agentes Claude Elite - ChinginGenerator v4 PRO

## ¿Qué son los Agentes Claude Elite?

Sistema de **17 agentes especializados** para maximizar la calidad y eficiencia en el desarrollo de tu proyecto ChinginGenerator.

## Agentes Disponibles

### Core Agents (7) - Fundamentales
- **architect**: Diseña arquitectura de nómina japonesa
- **critic**: Cuestiona decisiones, encuentra fallas en cálculos
- **explorer**: Investiga código y archivos Excel existentes
- **memory**: Recuerda contexto entre sesiones
- **coder**: Implementa código siguiendo el plan
- **tester**: Verifica visualmente con Playwright
- **stuck**: Escala al humano cuando hay problemas

### Quality Agents (4) - Calidad y Seguridad
- **security**: Audita OWASP, protege datos personales
- **debugger**: Encuentra causa raíz de bugs
- **reviewer**: Code review, SOLID, clean code
- **performance**: Optimiza Core Web Vitals

### Domain Agents (6) - Especialistas
- **frontend**: HTML, CSS, Jinja2, UI/UX japonesa
- **backend**: Flask, APIs, REST, autenticación
- **database**: SQLite, optimización, queries
- **data-sync**: Excel→DB, Access→DB, CSV, JSON
- **devops**: Docker, CI/CD, GitHub Actions
- **api-designer**: OpenAPI, Swagger, REST design

## Uso Recomendado

### Para Nueva Funcionalidad
```
1. memory → "Recuerda contexto del proyecto ChinginGenerator"
2. architect → "Diseña solución para [nueva funcionalidad]"
3. critic → "Cuestiona el diseño anterior"
4. explorer → "Investiga código existente relacionado"
5. coder → "Implementa la solución"
6. reviewer → "Revisa el código implementado"
7. tester → "Verifica visualmente el resultado"
```

### Para Corrección de Bugs
```
1. memory → "Recuerda bugs similares y soluciones"
2. debugger → "Analiza el problema paso a paso"
3. explorer → "Investiga el área afectada"
4. coder → "Implementa la corrección"
5. tester → "Verifica la solución"
```

### Para Procesamiento de Datos
```
1. memory → "Recuerda formatos japoneses de Excel"
2. data-sync → "Analiza estructura de archivos maestros"
3. database → "Optimiza consultas SQL"
4. backend → "Implementa procesamiento"
5. tester → "Verifica con datos reales"
```

## Workflows Predefinidos

El sistema incluye workflows automáticos:

- **new_feature**: ["memory", "architect", "critic", "explorer", "coder", "reviewer", "tester"]
- **bug_fix**: ["memory", "debugger", "explorer", "coder", "tester"]
- **data_migration**: ["memory", "data-sync", "database", "tester"]
- **api_development**: ["memory", "api-designer", "critic", "backend", "security", "tester"]
- **deployment**: ["memory", "security", "devops", "tester"]

## Configuración Específica para ChinginGenerator

### Memoria del Proyecto
Archivo: `.claude/memory/project.md`

Contiene:
- **Estructura de la base de datos** SQLite
- **Cálculos de nómina japonesa** (賃金台帳)
- **Formatos de Excel** maestros (派遣社員, 請負社員)
- **Requisitos legales** japoneses
- **Issues comunes** y soluciones

### Permisos Configurados
Los agentes tienen permisos para:
- Ejecutar `python run.py`
- Iniciar servidor Flask
- Manipular archivos Excel
- Acceder a base de datos SQLite
- Probar con Playwright

## Ejemplos de Uso

### Ejemplo 1: Nuevo Cálculo de Nómina
```
Usuario: "Necesito agregar cálculo de bono por antigüedad"

Sistema automáticamente invoca:
1. memory → Recuerda cálculos existentes
2. architect → Diseña integración del bono
3. critic → Verifica impacto en otros cálculos
4. data-sync → Analiza dónde obtener datos de antigüedad
5. coder → Implementa nueva lógica
6. reviewer → Verifica código
7. tester → Prueba con datos reales
```

### Ejemplo 2: Optimización de Procesamiento
```
Usuario: "El procesamiento de 1000 empleados es muy lento"

Sistema automáticamente invoca:
1. memory → Recuerda optimizaciones previas
2. performance → Analiza cuellos de botella
3. database → Optimiza queries SQL
4. backend → Mejora algoritmos
5. tester → Verifica mejoras
```

## Principios Clave

### Sin Fallbacks
- Cuando cualquier agente encuentra un problema, **DEBE** invocar a `stuck`
- No se permiten workarounds ni suposiciones
- El humano siempre tiene la decisión final

### Opus para Pensar, Sonnet para Ejecutar
- **Opus (14 agentes)**: Decisiones arquitecturales, análisis profundo
- **Sonnet (3 agentes)**: Implementación, testing, escalación

### Memory Persistente
- `memory` mantiene contexto entre sesiones
- Registra decisiones, errores, preferencias
- Aprende de cada interacción

## Archivos Importantes

- `.claude/agents/`: Definiciones de los 17 agentes
- `.claude/agents-registry.json`: Configuración y routing
- `.claude/memory/project.md`: Memoria específica del proyecto
- `.claude/settings.local.json`: Permisos y configuración local

## Integración con Git

Los agentes están configurados para trabajar con tu repositorio:
- Ignoran archivos generados (outputs/, backups/)
- Pueden ejecutar comandos Git
- Respetan el .gitignore existente

## Soporte Específico para Nómina Japonesa

Los agentes conocen:
- **Cálculos estándar**: 基本給, 残業手当, 深夜手当
- **Deducciones**: 健康保険料, 厚年金料, 雇用保険料
- **Formatos**: 賃金台帳, 派遣社員, 請負社員
- **Requisitos legales**: 労働基準法, 健康保険法

---

**17 agentes especializados. Cero fallbacks. Máxima calidad para tu ChinginGenerator.**