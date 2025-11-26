#!/bin/bash
# ========================================
# ChinginGenerator v4 PRO - Docker Scripts
# Sistema de Nóminas Japonesas 賃金台帳
# ========================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Nombres únicos
IMAGE_NAME="chingin-generator-v4-pro"
CONTAINER_NAME="chingin-generator-app"
COMPOSE_PROJECT="chingin"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  賃金台帳 Generator v4 PRO - Docker   ${NC}"
echo -e "${BLUE}========================================${NC}"

case "$1" in
    build)
        echo -e "${YELLOW}🔨 Construyendo imagen ${IMAGE_NAME}...${NC}"
        docker build -t ${IMAGE_NAME}:latest .
        echo -e "${GREEN}✓ Imagen construida${NC}"
        ;;
    
    up)
        echo -e "${YELLOW}🚀 Iniciando contenedores...${NC}"
        docker-compose -p ${COMPOSE_PROJECT} up -d
        echo -e "${GREEN}✓ Contenedores iniciados${NC}"
        echo -e "${BLUE}📍 Accede a: http://localhost:8989${NC}"
        ;;
    
    down)
        echo -e "${YELLOW}🛑 Deteniendo contenedores...${NC}"
        docker-compose -p ${COMPOSE_PROJECT} down
        echo -e "${GREEN}✓ Contenedores detenidos${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Reiniciando contenedores...${NC}"
        docker-compose -p ${COMPOSE_PROJECT} restart
        echo -e "${GREEN}✓ Contenedores reiniciados${NC}"
        ;;
    
    logs)
        echo -e "${BLUE}📋 Logs del contenedor:${NC}"
        docker logs -f ${CONTAINER_NAME}
        ;;
    
    status)
        echo -e "${BLUE}📊 Estado de contenedores:${NC}"
        docker ps -a --filter "name=${CONTAINER_NAME}"
        echo ""
        echo -e "${BLUE}📦 Volúmenes:${NC}"
        docker volume ls --filter "name=chingin"
        echo ""
        echo -e "${BLUE}🌐 Redes:${NC}"
        docker network ls --filter "name=chingin"
        ;;
    
    clean)
        echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará contenedores, imágenes y volúmenes${NC}"
        read -p "¿Estás seguro? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo -e "${YELLOW}🧹 Limpiando recursos Docker...${NC}"
            docker-compose -p ${COMPOSE_PROJECT} down -v --rmi all
            docker volume rm chingin_database_v4 chingin_uploads_v4 chingin_outputs_v4 chingin_backups_v4 2>/dev/null
            echo -e "${GREEN}✓ Limpieza completada${NC}"
        else
            echo -e "${BLUE}Operación cancelada${NC}"
        fi
        ;;
    
    shell)
        echo -e "${BLUE}🐚 Entrando al contenedor...${NC}"
        docker exec -it ${CONTAINER_NAME} /bin/bash
        ;;
    
    backup)
        echo -e "${YELLOW}💾 Creando backup de volúmenes...${NC}"
        BACKUP_DIR="./docker_backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p ${BACKUP_DIR}
        
        # Backup de base de datos
        docker run --rm -v chingin_database_v4:/data -v $(pwd)/${BACKUP_DIR}:/backup alpine tar cvf /backup/database.tar /data
        
        # Backup de uploads
        docker run --rm -v chingin_uploads_v4:/data -v $(pwd)/${BACKUP_DIR}:/backup alpine tar cvf /backup/uploads.tar /data
        
        # Backup de outputs
        docker run --rm -v chingin_outputs_v4:/data -v $(pwd)/${BACKUP_DIR}:/backup alpine tar cvf /backup/outputs.tar /data
        
        # Backup de backups
        docker run --rm -v chingin_backups_v4:/data -v $(pwd)/${BACKUP_DIR}:/backup alpine tar cvf /backup/backups.tar /data
        
        echo -e "${GREEN}✓ Backup guardado en: ${BACKUP_DIR}${NC}"
        ;;
    
    *)
        echo -e "${BLUE}Uso: $0 {comando}${NC}"
        echo ""
        echo "Comandos disponibles:"
        echo "  build    - Construir imagen Docker"
        echo "  up       - Iniciar contenedores"
        echo "  down     - Detener contenedores"
        echo "  restart  - Reiniciar contenedores"
        echo "  logs     - Ver logs en tiempo real"
        echo "  status   - Ver estado de contenedores y volúmenes"
        echo "  clean    - Eliminar todo (contenedores, imágenes, volúmenes)"
        echo "  shell    - Entrar al contenedor"
        echo "  backup   - Crear backup de volúmenes"
        ;;
esac
