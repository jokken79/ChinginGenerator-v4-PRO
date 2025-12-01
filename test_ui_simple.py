#!/usr/bin/env python3
"""Prueba manual con Playwright para la interfaz moderna."""
import os
import sys

import pytest

if os.environ.get("CI") or not sys.stdin.isatty():
    pytest.skip("Prueba UI manual: requiere entorno interactivo con navegador", allow_module_level=True)

# El código original se mantiene para ejecuciones manuales
import asyncio
import time
from playwright.async_api import async_playwright


async def test_ui():
    """Probar la interfaz con Playwright - Version simplificada"""

    def find_available_port(start_port=8001):
        import socket

        port = start_port
        while port < 8100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    return port
            except OSError:
                port += 1
        return start_port

    puerto = find_available_port()
    print(f"Iniciando pruebas en puerto {puerto}")

    import subprocess

    env = os.environ.copy()
    env["PORT"] = str(puerto)
    env["ENHANCED_UI"] = "true"

    process = subprocess.Popen([sys.executable, "app.py"], env=env)

    print("Esperando a que la aplicación inicie...")
    await asyncio.sleep(5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = f"http://localhost:{puerto}?enhanced=true"
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            await page.screenshot(path="test_screenshot_full.png", full_page=True)
        finally:
            await browser.close()
            process.terminate()


if __name__ == "__main__":
    asyncio.run(test_ui())
