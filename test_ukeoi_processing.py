#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueba de procesamiento para archivos 請負社員 en formato vertical.

El archivo de ejemplo solo está disponible en entornos locales, por lo que la
prueba se omite automáticamente cuando no se encuentra.
"""
import os
import sys

import pytest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_processor import ExcelProcessor
from database import get_all_employees, get_payroll_by_employee

SAMPLE_FILE = r"C:\\Users\\JPUNS\\Desktop\\Crear Chingi 25.11.17 docs\\JPNuevo\\給与明細(派遣社員)2025.1(0217支給).xlsm"

if not os.path.exists(SAMPLE_FILE):
    pytest.skip(
        f"Archivo de ejemplo no disponible: {SAMPLE_FILE}", allow_module_level=True
    )


def test_ukeoi_processing_with_sample_file():
    """Procesar el archivo de ejemplo y verificar datos mínimos en la BD."""
    processor = ExcelProcessor()

    result = processor.process_file(SAMPLE_FILE)
    assert "error" not in result

    summary = processor.get_summary()
    assert summary["total_records"] > 0

    employees = get_all_employees()
    ukeoi_employees = [emp for emp in employees if emp["employee_id"].startswith("03")]
    assert ukeoi_employees, "Se esperaba al menos un empleado 請負社員"

    first_emp = ukeoi_employees[0]["employee_id"]
    records = get_payroll_by_employee(first_emp)
    assert records, "El empleado de ejemplo debe tener registros de nómina"
