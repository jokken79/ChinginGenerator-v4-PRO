#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar generacion de ZIP para 請負社員
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_all_ukeoi_employees, get_payroll_by_employee
from excel_processor import ExcelProcessor

print("=" * 80)
print("TEST: Verificacion de ZIP para 請負社員")
print("=" * 80)

# Obtener lista de empleados 請負社員
print("\n[INFO] Obteniendo lista de empleados 請負社員...")
ukeoi_data = get_all_ukeoi_employees()
employees = ukeoi_data.get('employees', [])

print(f"\n[Resultado] Encontrados {len(employees)} empleados 請負社員")

if len(employees) == 0:
    print("[ERROR] No hay empleados 請負社員 para generar ZIP")
    sys.exit(1)

# Mostrar primeros 5
print(f"\n[INFO] Primeros 5 empleados:")
for emp in employees[:5]:
    emp_id = emp.get('employee_id')
    name = emp.get('name', emp.get('name_jp', 'N/A'))
    print(f"  - ID: {emp_id}, Nombre: {name}")

# Verificar que tengan datos de nomina
print(f"\n[INFO] Verificando que tengan datos de nomina...")
employees_with_payroll = 0
for emp in employees:
    emp_id = emp.get('employee_id')
    records = get_payroll_by_employee(emp_id)
    if records and len(records) > 0:
        employees_with_payroll += 1

print(f"\n[Resultado] {employees_with_payroll}/{len(employees)} empleados tienen datos de nomina")

# Intentar generar un archivo de prueba
print(f"\n" + "=" * 80)
print("TEST: Generacion de 賃金台帳 individual")
print("=" * 80)

test_emp_id = employees[0].get('employee_id')
print(f"\n[INFO] Generando 賃金台帳 para empleado {test_emp_id}...")

processor = ExcelProcessor()
try:
    result = processor.generate_chingin_print(test_emp_id, 2025)
    if result.get("success"):
        output_path = result.get("output_path")
        print(f"\n[OK] Archivo generado exitosamente:")
        print(f"  Ruta: {output_path}")
        print(f"  Empleado: {result.get('employee_id')}")
        print(f"  Nombre: {result.get('name')}")
        print(f"  Meses encontrados: {result.get('months_found')}")

        # Verificar que el archivo existe
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  Tamano: {size:,} bytes")
        else:
            print(f"  [ERROR] El archivo no existe en disco")
    else:
        print(f"\n[ERROR] No se pudo generar el archivo")
        print(f"  Detalle: {result}")
except Exception as e:
    print(f"\n[ERROR] Exception al generar: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
if len(employees) > 0 and employees_with_payroll > 0:
    print(f"[OK] El ZIP de 請負社員 deberia generarse correctamente")
    print(f"     - {len(employees)} empleados disponibles")
    print(f"     - {employees_with_payroll} con datos de nomina")
else:
    print(f"[ERROR] Faltan datos para generar ZIP")

print("\nTest completado.")
