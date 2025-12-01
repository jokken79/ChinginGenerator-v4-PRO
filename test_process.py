#!/usr/bin/env python3
"""Prueba de procesamiento básica con archivo de ejemplo."""
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


def test_process_file_sample():
    processor = ExcelProcessor()
    result = processor.process_file(SAMPLE_FILE)
    assert "error" not in result

    summary = processor.get_summary()
    assert summary["total_records"] > 0
