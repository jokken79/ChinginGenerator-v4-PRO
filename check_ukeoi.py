#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('chingin_data.db')
cursor = conn.cursor()

# Contar registros de empleados 請負社員 (IDs que empiezan con 03)
cursor.execute("SELECT COUNT(*) FROM payroll_records WHERE employee_id LIKE '03%'")
count = cursor.fetchone()[0]
print(f"Registros de nomina con employee_id 03xxxx: {count}")

# Obtener ejemplos
cursor.execute("SELECT DISTINCT employee_id FROM payroll_records WHERE employee_id LIKE '03%' LIMIT 5")
examples = [row[0] for row in cursor.fetchall()]
print(f"Ejemplos de IDs: {examples}")

# Contar total de empleados 請負 en maestro
cursor.execute("SELECT COUNT(*) FROM ukeoi_employees")
total_ukeoi = cursor.fetchone()[0]
print(f"Total empleados en ukeoi_employees: {total_ukeoi}")

# Contar empleados con datos
cursor.execute("""
SELECT COUNT(DISTINCT u.employee_id)
FROM ukeoi_employees u
INNER JOIN payroll_records p ON u.employee_id = p.employee_id
""")
with_data = cursor.fetchone()[0]
print(f"Empleados 請負 con registros de nomina: {with_data}")

conn.close()
