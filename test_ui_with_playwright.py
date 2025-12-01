#!/usr/bin/env python3
"""Prueba manual completa con Playwright."""
import os
import sys

import pytest

if os.environ.get("CI") or not sys.stdin.isatty():
    pytest.skip("Prueba UI manual: requiere entorno interactivo con navegador", allow_module_level=True)

# Código original para ejecuciones manuales
import asyncio
from playwright.async_api import async_playwright


async def test_ui_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto("http://localhost:8000/?theme=moderno")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="playwright_screenshot.png", full_page=True)
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_ui_with_playwright())
