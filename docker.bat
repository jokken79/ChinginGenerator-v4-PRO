@echo off
REM ========================================
REM ChinginGenerator v4 PRO - Docker Scripts
REM Sistema de Nóminas Japonesas
REM ========================================

setlocal enabledelayedexpansion

REM Nombres únicos
set IMAGE_NAME=chingin-generator-v4-pro
set CONTAINER_NAME=chingin-generator-app
set COMPOSE_PROJECT=chingin

echo ========================================
echo   賃金台帳 Generator v4 PRO - Docker
echo ========================================
echo.

if "%1"=="" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
if "%1"=="shell" goto shell
goto help

:build
echo [BUILD] Construyendo imagen %IMAGE_NAME%...
docker build -t %IMAGE_NAME%:latest .
echo [OK] Imagen construida
goto end

:up
echo [START] Iniciando contenedores...
docker-compose -p %COMPOSE_PROJECT% up -d
echo [OK] Contenedores iniciados
echo.
echo Accede a: http://localhost:8989
goto end

:down
echo [STOP] Deteniendo contenedores...
docker-compose -p %COMPOSE_PROJECT% down
echo [OK] Contenedores detenidos
goto end

:restart
echo [RESTART] Reiniciando contenedores...
docker-compose -p %COMPOSE_PROJECT% restart
echo [OK] Contenedores reiniciados
goto end

:logs
echo [LOGS] Mostrando logs...
docker logs -f %CONTAINER_NAME%
goto end

:status
echo [STATUS] Estado de contenedores:
docker ps -a --filter "name=%CONTAINER_NAME%"
echo.
echo [VOLUMES] Volumenes:
docker volume ls --filter "name=chingin"
echo.
echo [NETWORKS] Redes:
docker network ls --filter "name=chingin"
goto end

:clean
echo [WARNING] Esto eliminara contenedores, imagenes y volumenes
set /p confirm="Estas seguro? (y/N): "
if /i "%confirm%"=="y" (
    echo [CLEAN] Limpiando recursos Docker...
    docker-compose -p %COMPOSE_PROJECT% down -v --rmi all
    docker volume rm chingin_database_v4 chingin_uploads_v4 chingin_outputs_v4 chingin_backups_v4 2>nul
    echo [OK] Limpieza completada
) else (
    echo Operacion cancelada
)
goto end

:shell
echo [SHELL] Entrando al contenedor...
docker exec -it %CONTAINER_NAME% /bin/bash
goto end

:help
echo Uso: docker.bat {comando}
echo.
echo Comandos disponibles:
echo   build    - Construir imagen Docker
echo   up       - Iniciar contenedores
echo   down     - Detener contenedores
echo   restart  - Reiniciar contenedores
echo   logs     - Ver logs en tiempo real
echo   status   - Ver estado de contenedores y volumenes
echo   clean    - Eliminar todo (contenedores, imagenes, volumenes)
echo   shell    - Entrar al contenedor
echo.
echo Ejemplos:
echo   docker.bat build
echo   docker.bat up
echo   docker.bat logs
goto end

:end
endlocal
