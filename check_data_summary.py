#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('chingin_data.db')
cursor = conn.cursor()

# Ver patrones de IDs con datos
cursor.execute("""
SELECT
    SUBSTR(employee_id, 1, 2) as prefix,
    COUNT(*) as total,
    COUNT(DISTINCT employee_id) as unique_employees
FROM payroll_records
GROUP BY SUBSTR(employee_id, 1, 2)
ORDER BY total DESC
LIMIT 10
""")

print("Patrones de employee_id con datos de nomina:")
print("-" * 60)
for row in cursor.fetchall():
    prefix, total, unique = row
    print(f"  IDs {prefix}xxxx: {total} registros, {unique} empleados unicos")

# Verificar tipos
cursor.execute("SELECT COUNT(*) FROM haken_employees")
total_haken = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(DISTINCT h.employee_id)
FROM haken_employees h
INNER JOIN payroll_records p ON h.employee_id = p.employee_id
""")
haken_with_data = cursor.fetchone()[0]

print(f"\nEmpleados 派遣社員:")
print(f"  Total registrados: {total_haken}")
print(f"  Con datos de nomina: {haken_with_data}")

conn.close()
