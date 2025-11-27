#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar el procesamiento de 請負社員 del formato vertical
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_processor import ExcelProcessor
from database import get_all_employees, get_payroll_by_employee

print("=" * 80)
print("TEST: Procesamiento de 請負社員 (formato vertical)")
print("=" * 80)

# Path al archivo de prueba
file_path = r"C:\Users\JPUNS\Desktop\Crear Chingi 25.11.17 docs\JPNuevo\給与明細(派遣社員)2025.1(0217支給).xlsm"

if not os.path.exists(file_path):
    print(f"[ERROR] Archivo no encontrado: {file_path}")
    sys.exit(1)

# Crear procesador
processor = ExcelProcessor()

# Procesar archivo
print(f"\n[Procesando] {os.path.basename(file_path)}")
result = processor.process_file(file_path)

print(f"\n[Resultado] {result}")

# Obtener resumen
summary = processor.get_summary()
print(f"\n" + "=" * 80)
print("RESUMEN:")
print("=" * 80)
print(f"  Total registros: {summary['total_records']}")
print(f"  Empleados unicos: {summary['unique_employees']}")
print(f"  Periodos: {summary['periods']}")

# Buscar empleados 請負社員 (IDs 03xxxx)
employees = get_all_employees()
ukeoi_employees = [emp for emp in employees if emp['employee_id'].startswith('03')]
haken_employees = [emp for emp in employees if not emp['employee_id'].startswith('03')]

print(f"\n" + "=" * 80)
print("EMPLEADOS POR TIPO:")
print("=" * 80)
print(f"  派遣社員 (20-25xxxx): {len(haken_employees)}")
print(f"  請負社員 (03xxxx): {len(ukeoi_employees)}")

# Mostrar primeros 5 empleados 請負社員
print(f"\n[INFO] Primeros 5 empleados 請負社員:")
for emp in ukeoi_employees[:5]:
    emp_id = emp['employee_id']
    records = get_payroll_by_employee(emp_id)
    print(f"  - ID: {emp_id}, Nombre: {emp.get('name_jp', 'N/A')}, Registros: {len(records)}")

# Verificar datos detallados de un empleado
if ukeoi_employees:
    test_emp_id = ukeoi_employees[0]['employee_id']
    print(f"\n" + "=" * 80)
    print(f"DATOS DETALLADOS DEL EMPLEADO {test_emp_id}:")
    print("=" * 80)
    records = get_payroll_by_employee(test_emp_id)
    if records:
        rec = records[0]
        print(f"  Nombre: {rec.get('name_jp', 'N/A')}")
        print(f"  Periodo: {rec.get('period', 'N/A')}")
        print(f"  Dias trabajados: {rec.get('work_days', 0)}")
        print(f"  Horas trabajadas: {rec.get('work_hours', 0)}")
        print(f"  Horas extra: {rec.get('overtime_hours', 0)}")
        print(f"  Horas nocturnas: {rec.get('night_hours', 0)}")
        print(f"  Salario base: {rec.get('base_pay', 0):,}")
        print(f"  Pago horas extra: {rec.get('overtime_pay', 0):,}")
        print(f"  Pago nocturno: {rec.get('night_pay', 0):,}")
        print(f"  Total pago: {rec.get('total_pay', 0):,}")
        print(f"  Pago neto: {rec.get('net_pay', 0):,}")

print(f"\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
if len(ukeoi_employees) > 0:
    print(f"[OK] Se procesaron {len(ukeoi_employees)} empleados 請負社員 correctamente")
else:
    print(f"[ERROR] NO se encontraron empleados 請負社員 en la base de datos")

print("\nTest completado.")
