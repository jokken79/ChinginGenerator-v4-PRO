# ========================================
# ChinginGenerator v4 PRO - Dockerfile
# Sistema de Nóminas Japonesas 賃金台帳
# ========================================

FROM python:3.11-slim

# Etiquetas para identificar la imagen
LABEL maintainer="jokken79"
LABEL app.name="chingin-generator-v4-pro"
LABEL app.version="4.0.0"
LABEL app.description="Sistema de Nóminas Japonesas - 賃金台帳 Generator"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app
ENV PORT=8989

# Crear directorio de trabajo
WORKDIR ${APP_HOME}

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY app.py .
COPY database.py .
COPY excel_processor.py .
COPY run.py .

# Copiar directorios
COPY templates/ templates/
COPY static/ static/

# Crear directorios necesarios con permisos
RUN mkdir -p data uploads outputs backups && \
    chmod 755 data uploads outputs backups

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash chingin && \
    chown -R chingin:chingin ${APP_HOME}

# Cambiar a usuario no-root
USER chingin

# Exponer puerto
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health')" || exit 1

# Comando de inicio
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8989"]
