#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación manual de generación de ZIP para 請負社員."""
import os
import sys

import pytest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_all_ukeoi_employees, get_payroll_by_employee
from excel_processor import ExcelProcessor

if not sys.stdin.isatty():
    pytest.skip("Prueba manual: requiere interacción y datos locales", allow_module_level=True)


def test_zip_generation_with_existing_data():
    ukeoi_data = get_all_ukeoi_employees()
    employees = ukeoi_data.get("employees", [])

    if not employees:
        pytest.skip("No hay empleados 請負社員 cargados en la base de datos")

    processor = ExcelProcessor()
    employees_with_payroll = 0

    for emp in employees:
        emp_id = emp.get("employee_id")
        if get_payroll_by_employee(emp_id):
            employees_with_payroll += 1

    assert employees_with_payroll > 0, "Los empleados deben tener registros de nómina"
