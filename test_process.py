#!/usr/bin/env python3
"""Test del procesador"""
from excel_processor import ExcelProcessor
import os

filepath = r"C:\Users\JPUNS\Desktop\Crear Chingi 25.11.17 docs\JPNuevo\給与明細(派遣社員)2025.1(0217支給).xlsm"

print("=== Probando procesamiento de archivo ===")
print(f"Archivo: {os.path.basename(filepath)}")

processor = ExcelProcessor()
result = processor.process_file(filepath)
print(f"\nResultado: {result}")

# Ver resumen
summary = processor.get_summary()
print(f"\n📊 Resumen:")
print(f"   Total registros: {summary['total_records']}")
print(f"   Empleados únicos: {summary['unique_employees']}")
print(f"   Periodos: {summary['periods']}")

# Ver algunos datos
data = processor.get_all_data()
if data:
    print(f"\n👥 Primeros 5 registros:")
    for rec in data[:5]:
        print(f"   {rec['employee_id']}: {rec['name_jp']} - ¥{rec['net_pay']:,.0f}")
