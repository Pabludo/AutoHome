"""Idealista login + scraping test — 2-step auth flow."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autohome.config import get_settings


async def main():
    from playwright.async_api import async_playwright

    settings = get_settings()
    screenshots = Path(__file__).parent.parent / "data" / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    print("=== IDEALISTA LOGIN TEST (2-step) ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # Step 1: Go to login
        print("1. Navegando a login...")
        await page.goto("https://www.idealista.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # Accept cookies
        try:
            accept = page.locator('#didomi-notice-agree-button')
            if await accept.is_visible(timeout=3000):
                print("   Aceptando cookies...")
                await accept.click()
                await asyncio.sleep(2)
        except Exception:
            pass

        # Step 2: Fill email
        print("2. Rellenando email...")
        await page.fill('input[name="email"]', settings.idealista_email)
        await asyncio.sleep(1)
        await page.screenshot(path=str(screenshots / "login_01_email.png"))

        # Step 3: Click Continuar
        print("3. Click Continuar...")
        await page.click('button:has-text("Continuar")')

        # Step 4: Wait for password field
        print("4. Esperando campo de contraseña...")
        try:
            await page.wait_for_selector('input[type="password"]', timeout=10000)
            print("   ✓ Campo de contraseña encontrado")
            await asyncio.sleep(1)
            await page.screenshot(path=str(screenshots / "login_02_password.png"))

            # Step 5: Fill password
            print("5. Rellenando contraseña...")
            await page.fill('input[type="password"]', settings.idealista_password)
            await asyncio.sleep(1)

            # Step 6: Click Iniciar sesión
            print("6. Click 'Iniciar sesión'...")
            await page.click('button:has-text("Iniciar sesión")')
            await asyncio.sleep(6)

            post_url = page.url
            print(f"   Post-login URL: {post_url}")
            await page.screenshot(path=str(screenshots / "login_03_result.png"))

            if "/login" not in post_url:
                print("   ✓ LOGIN EXITOSO — Redirigido fuera de /login")
            else:
                print("   ⚠ Posiblemente no logueado — seguimos en /login")
                # Check for error messages
                error = await page.query_selector('.error-message, [class*="error"]')
                if error:
                    err_text = await error.inner_text()
                    print(f"   Error: {err_text}")

        except Exception as e:
            print(f"   ✗ Error esperando contraseña: {e}")
            await page.screenshot(path=str(screenshots / "login_02_error.png"))

        # Step 7: Navigate to "Mis anuncios" area (where stats are visible)
        print("\n7. Navegando a zona de propietario...")
        try:
            await page.goto("https://www.idealista.com/user/my-adverts/", wait_until="domcontentloaded")
            await asyncio.sleep(4)
            my_url = page.url
            print(f"   URL: {my_url}")
            await page.screenshot(path=str(screenshots / "login_04_my_adverts.png"))

            # Look for any property listings
            adverts = await page.query_selector_all('[class*="advert"], [class*="listing"], .item-info')
            print(f"   Anuncios encontrados: {len(adverts)}")

            # Dump page text for analysis
            text = await page.inner_text("body")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            print("   Contenido relevante:")
            for line in lines[:30]:
                if len(line) > 5:
                    print(f"     {line[:150]}")

        except Exception as e:
            print(f"   Error: {e}")

        # Step 8: Try the stats page directly
        print("\n8. Intentando página de estadísticas...")
        try:
            await page.goto("https://www.idealista.com/user/my-adverts/stats/", wait_until="domcontentloaded")
            await asyncio.sleep(4)
            stats_url = page.url
            print(f"   URL: {stats_url}")
            await page.screenshot(path=str(screenshots / "login_05_stats.png"))

            text = await page.inner_text("body")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            print("   Contenido:")
            for line in lines[:30]:
                if len(line) > 5:
                    print(f"     {line[:150]}")

        except Exception as e:
            print(f"   Error: {e}")

        print("\n   Esperando 10s para inspección visual...")
        await asyncio.sleep(10)
        await browser.close()

    print("\n✓ Test completado")
    print(f"  Screenshots: {screenshots}")


if __name__ == "__main__":
    asyncio.run(main())
