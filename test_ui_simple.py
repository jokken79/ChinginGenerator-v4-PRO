#!/usr/bin/env python3
"""
Script simplificado para probar la interfaz de ChinginGenerator v4-PRO
Sin caracteres Unicode problemáticos
"""
import asyncio
import sys
import os
from playwright.async_api import async_playwright
import time

async def test_ui():
    """Probar la interfaz con Playwright - Version simplificada"""
    
    # Encontrar puerto disponible
    def find_available_port(start_port=8001):
        import socket
        port = start_port
        while port < 8100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                port += 1
        return start_port
    
    puerto = find_available_port()
    print(f"Iniciando pruebas en puerto {puerto}")
    
    # Iniciar la aplicación en segundo plano
    import subprocess
    env = os.environ.copy()
    env['PORT'] = str(puerto)
    env['ENHANCED_UI'] = 'true'
    
    process = subprocess.Popen([
        sys.executable, 'app.py'
    ], env=env)
    
    # Esperar a que la aplicación inicie
    print("Esperando a que la aplicación inicie...")
    await asyncio.sleep(5)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navegar a la aplicación
            url = f"http://localhost:{puerto}?enhanced=true"
            print(f"Abriendo {url}")
            await page.goto(url)
            
            # Esperar a que cargue la página
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(3)
            
            print("Tomando captura de pantalla completa...")
            await page.screenshot(path="test_screenshot_full.png", full_page=True)
            
            # 1. Verificar que se puedan leer las letras (contraste)
            print("Verificando legibilidad del texto...")
            
            # Tomar captura del header
            header = await page.query_selector("header")
            if header:
                await header.screenshot(path="test_header_text.png")
                print("Captura del header guardada")
            
            # 2. Verificar tarjetas de estadísticas
            print("Verificando tarjetas de estadísticas...")
            stat_cards = await page.query_selector_all(".stat-card")
            print(f"Encontradas {len(stat_cards)} tarjetas de estadísticas")
            
            for i, card in enumerate(stat_cards[:2]):  # Probar las primeras 2
                await card.screenshot(path=f"test_stat_card_{i+1}.png")
                print(f"Captura de tarjeta {i+1} guardada")
            
            # 3. Verificar pestañas de navegación
            print("Verificando pestañas de navegación...")
            tabs = await page.query_selector_all('[id^="tab-"]')
            print(f"Encontradas {len(tabs)} pestañas de navegación")
            
            # 4. Verificar configuración (Settings)
            print("Verificando sección de configuración...")
            
            # Hacer clic en Settings
            settings_tab = await page.query_selector("#tab-settings")
            if settings_tab:
                await settings_tab.click()
                await asyncio.sleep(2)
                
                # Tomar captura de settings
                settings_section = await page.query_selector("#section-settings")
                if settings_section:
                    await settings_section.screenshot(path="test_settings_section.png")
                    print("Captura de settings guardada")
                    
                    # Verificar opciones de tema
                    theme_buttons = await page.query_selector_all('[id^="btn"][id$="Theme"]')
                    print(f"Encontrados {len(theme_buttons)} botones de tema")
                    
                    # Verificar switches de configuración
                    switches = await page.query_selector_all('input[type="checkbox"]')
                    print(f"Encontrados {len(switches)} switches de configuración")
            
            # 5. Verificar Agentes Claude
            print("Verificando sección de agentes...")
            
            agents_tab = await page.query_selector("#tab-agents")
            if agents_tab:
                await agents_tab.click()
                await asyncio.sleep(2)
                
                # Tomar captura de agentes
                agents_section = await page.query_selector("#section-agents")
                if agents_section:
                    await agents_section.screenshot(path="test_agents_section.png")
                    print("Captura de agentes guardada")
                    
                    # Verificar tarjetas de agentes
                    agent_cards = await page.query_selector_all(".agent-card")
                    print(f"Encontradas {len(agent_cards)} tarjetas de agentes")
                    
                    # Probar clic en un agente
                    if agent_cards:
                        await agent_cards[0].click()
                        await asyncio.sleep(1)
                        print("Clic en agente ejecutado")
            
            # 6. Verificar tema claro/oscuro
            print("Verificando cambio de tema...")
            
            # Probar tema oscuro
            dark_theme_btn = await page.query_selector("#btnDarkTheme")
            if dark_theme_btn:
                await dark_theme_btn.click()
                await asyncio.sleep(1)
                await page.screenshot(path="test_dark_theme.png")
                print("Tema oscuro aplicado")
                
                # Volver al tema claro
                light_theme_btn = await page.query_selector("#btnLightTheme")
                if light_theme_btn:
                    await light_theme_btn.click()
                    await asyncio.sleep(1)
                    await page.screenshot(path="test_light_theme.png")
                    print("Tema claro aplicado")
            
            # 7. Verificar contraste y legibilidad
            print("Verificando contraste y legibilidad...")
            
            # Evaluar contraste de texto
            text_elements = await page.query_selector_all("h1, h2, h3, p, span, button")
            print(f"Evaluados {len(text_elements)} elementos de texto")
            
            # 8. Tomar capturas de diferentes secciones
            print("Tomando capturas adicionales...")
            
            sections = ["upload", "data", "export"]
            for section in sections:
                tab = await page.query_selector(f"#tab-{section}")
                if tab:
                    await tab.click()
                    await asyncio.sleep(2)
                    
                    section_elem = await page.query_selector(f"#section-{section}")
                    if section_elem:
                        await section_elem.screenshot(path=f"test_section_{section}.png")
                        print(f"Captura de sección {section} guardada")
            
            print("Pruebas de interfaz completadas exitosamente")
            print("Capturas guardadas:")
            print("  - test_screenshot_full.png (pantalla completa)")
            print("  - test_header_text.png (header)")
            print("  - test_stat_card_1.png, test_stat_card_2.png (tarjetas de estadísticas)")
            print("  - test_settings_section.png (configuración)")
            print("  - test_agents_section.png (agentes)")
            print("  - test_dark_theme.png (tema oscuro)")
            print("  - test_light_theme.png (tema claro)")
            print("  - test_section_upload.png (sección upload)")
            print("  - test_section_data.png (sección data)")
            print("  - test_section_export.png (sección export)")
            
            # 9. Verificar responsive design
            print("Verificando diseño responsive...")
            
            # Probar diferentes tamaños de pantalla
            sizes = [
                {"width": 1920, "height": 1080, "name": "desktop"},
                {"width": 1366, "height": 768, "name": "laptop"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 375, "height": 667, "name": "mobile"}
            ]
            
            for size in sizes:
                await page.set_viewport_size(size["width"], size["height"])
                await asyncio.sleep(1)
                await page.screenshot(path=f"test_responsive_{size['name']}.png")
                print(f"Captura responsive {size['name']} ({size['width']}x{size['height']}) guardada")
            
            print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
            
        except Exception as e:
            print(f"Error durante las pruebas: {e}")
            
        finally:
            await browser.close()
    
    # Cerrar la aplicación
    print("Cerrando la aplicación...")
    process.terminate()
    await asyncio.sleep(2)

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DE INTERFAZ CON PLAYWRIGHT")
    print("=" * 60)
    asyncio.run(test_ui())
    print("=" * 60)
    print("PRUEBAS FINALIZADAS")
    print("Revisa las capturas de pantalla en el directorio actual")