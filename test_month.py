#!/usr/bin/env python3
"""Test rápido para verificar agrupación por mes con archivo de ejemplo."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_processor import ExcelProcessor

SAMPLE_FILE = r"C:\\Users\\JPUNS\\Desktop\\Crear Chingi 25.11.17 docs\\JPNuevo\\給与明細(派遣社員)2025.1(0217支給).xlsm"

if not os.path.exists(SAMPLE_FILE):
    pytest.skip(
        f"Archivo de ejemplo no disponible: {SAMPLE_FILE}", allow_module_level=True
    )


def test_export_by_month(tmp_path):
    processor = ExcelProcessor()
    processor.process_file(SAMPLE_FILE)

    export_path = tmp_path / "TEST_Por_mes.xlsx"
    processor.export_by_month(str(export_path))

    assert export_path.exists()
