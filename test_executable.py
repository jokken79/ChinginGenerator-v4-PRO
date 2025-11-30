#!/usr/bin/env python3
"""Prueba manual para verificar que el ejecutable se inicie correctamente."""
import os
import sys

import pytest

EXE_PATH = "dist/ChinginGenerator.exe"

if not sys.stdin.isatty():
    pytest.skip("Prueba manual interactiva: requiere terminal", allow_module_level=True)

if not os.path.exists(EXE_PATH):
    pytest.skip(f"Ejecutable no disponible en {EXE_PATH}", allow_module_level=True)


def test_executable_launches():
    import subprocess
    import time

    process = subprocess.Popen([EXE_PATH])
    time.sleep(5)
    try:
        assert process.poll() is None, "El proceso se cerró inesperadamente"
    finally:
        process.terminate()
