#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidad para limpiar archivos antiguos en outputs/
"""
import sys
import io
import os
import time
from datetime import datetime, timedelta

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def cleanup_old_files(directory="outputs", days_old=7, dry_run=False):
    """
    Eliminar archivos más antiguos de X días

    Args:
        directory: Directorio a limpiar
        days_old: Edad mínima en días para eliminar
        dry_run: Si True, solo muestra qué archivos se eliminarían sin eliminarlos

    Returns:
        dict con estadísticas
    """
    if not os.path.exists(directory):
        return {"error": f"Directorio {directory} no existe"}

    cutoff_time = time.time() - (days_old * 86400)
    deleted_count = 0
    deleted_size = 0
    kept_count = 0
    errors = []

    print(f"🧹 Limpiando archivos en {directory} más antiguos de {days_old} días...")
    print(f"📅 Fecha límite: {datetime.fromtimestamp(cutoff_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'🔍 MODO DRY RUN - No se eliminará nada' if dry_run else '⚠️  MODO REAL - Se eliminarán archivos'}")
    print("=" * 80)

    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)

            try:
                file_mtime = os.path.getmtime(filepath)
                file_size = os.path.getsize(filepath)

                if file_mtime < cutoff_time:
                    file_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')

                    if dry_run:
                        print(f"🗑️  [DRY RUN] {filepath} ({file_size:,} bytes, {file_date})")
                    else:
                        os.remove(filepath)
                        print(f"✅ Eliminado: {filepath} ({file_size:,} bytes, {file_date})")

                    deleted_count += 1
                    deleted_size += file_size
                else:
                    kept_count += 1

            except Exception as e:
                errors.append(f"Error con {filepath}: {e}")
                print(f"❌ Error: {filepath} - {e}")

    # Eliminar directorios vacíos
    if not dry_run:
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"📁 Directorio vacío eliminado: {dir_path}")
                except Exception as e:
                    print(f"❌ Error eliminando directorio {dir_path}: {e}")

    print("=" * 80)
    print(f"📊 Resumen:")
    print(f"   {'Archivos que se eliminarían' if dry_run else 'Archivos eliminados'}: {deleted_count}")
    print(f"   Archivos conservados: {kept_count}")
    print(f"   Espacio {'que se liberaría' if dry_run else 'liberado'}: {deleted_size:,} bytes ({deleted_size / 1024 / 1024:.2f} MB)")
    print(f"   Errores: {len(errors)}")

    return {
        "deleted_count": deleted_count,
        "deleted_size": deleted_size,
        "kept_count": kept_count,
        "errors": errors,
        "dry_run": dry_run
    }

if __name__ == "__main__":
    import sys

    # Default: 7 días, dry run
    days = 7
    dry_run = True

    if len(sys.argv) > 1:
        days = int(sys.argv[1])

    if len(sys.argv) > 2 and sys.argv[2].lower() == "delete":
        dry_run = False
        print("⚠️  ADVERTENCIA: Ejecutando en MODO REAL - Se eliminarán archivos!")
        print("    Presiona Ctrl+C en los próximos 5 segundos para cancelar...")
        time.sleep(5)

    result = cleanup_old_files(days_old=days, dry_run=dry_run)

    if dry_run:
        print("\n💡 Para ejecutar la limpieza real, usa: python cleanup_old_files.py 7 delete")
