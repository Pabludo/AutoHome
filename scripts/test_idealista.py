"""Quick Idealista scraping test — headful browser for debugging."""

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

    print("=== IDEALISTA SCRAPING TEST ===")
    print(f"Email: {settings.idealista_email}")

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

        # Step 1: Navigate to main page
        print("\n1. Navegando a idealista.com...")
        await page.goto("https://www.idealista.com", wait_until="domcontentloaded")
        await asyncio.sleep(4)

        title = await page.title()
        print(f"   Título: {title}")
        await page.screenshot(path=str(screenshots / "01_landing.png"))

        # Check for cookie consent
        try:
            accept_btn = await page.query_selector(
                '#didomi-notice-agree-button, [id*="accept"], button:has-text("Aceptar")'
            )
            if accept_btn:
                print("   Aceptando cookies...")
                await accept_btn.click()
                await asyncio.sleep(2)
        except Exception:
            pass

        # Step 2: Go to login
        print("\n2. Navegando a login...")
        await page.goto("https://www.idealista.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(4)

        title = await page.title()
        url = page.url
        print(f"   Título: {title}")
        print(f"   URL: {url}")
        await page.screenshot(path=str(screenshots / "02_login_page.png"))

        # Dump all input fields for inspection
        inputs = await page.query_selector_all("input")
        print(f"   Inputs encontrados: {len(inputs)}")
        for inp in inputs:
            inp_type = await inp.get_attribute("type") or "?"
            inp_name = await inp.get_attribute("name") or "?"
            inp_id = await inp.get_attribute("id") or "?"
            inp_placeholder = await inp.get_attribute("placeholder") or "?"
            print(f"     type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder}")

        # Step 3: Try to fill login form
        print("\n3. Intentando login...")
        email_filled = False

        # Strategy 1: input[name="email"]
        for selector in [
            'input[name="email"]',
            'input[type="email"]',
            '#email',
            'input[id*="email"]',
            'input[placeholder*="mail"]',
        ]:
            el = await page.query_selector(selector)
            if el:
                print(f"   ✓ Email input: {selector}")
                await el.fill(settings.idealista_email)
                email_filled = True
                break

        if not email_filled:
            print("   ✗ No se encontró campo de email")
            print("   Posible bloqueo anti-bot antes del formulario")
            # Take full HTML dump for analysis
            html = await page.content()
            html_path = screenshots / "login_page.html"
            html_path.write_text(html, encoding="utf-8")
            print(f"   HTML guardado en: {html_path}")
        else:
            await asyncio.sleep(1)

            # Find password field
            for selector in [
                'input[name="password"]',
                'input[type="password"]',
                '#password',
            ]:
                el = await page.query_selector(selector)
                if el:
                    print(f"   ✓ Password input: {selector}")
                    await el.fill(settings.idealista_password)
                    break

            await asyncio.sleep(1)
            await page.screenshot(path=str(screenshots / "03_form_filled.png"))

            # Submit
            submit = await page.query_selector(
                'button[type="submit"], input[type="submit"], '
                'button:has-text("Entrar"), button:has-text("Iniciar")'
            )
            if submit:
                print("   Enviando formulario...")
                await submit.click()
                await asyncio.sleep(6)

                post_title = await page.title()
                post_url = page.url
                print(f"   Post-login título: {post_title}")
                print(f"   Post-login URL: {post_url}")
                await page.screenshot(path=str(screenshots / "04_post_login.png"))

        # Step 4: Try a public property page regardless of login status
        print("\n4. Navegando a propiedad de ejemplo...")
        test_url = "https://www.idealista.com/inmueble/111029821/"
        await page.goto(test_url, wait_until="domcontentloaded")
        await asyncio.sleep(4)

        prop_title = await page.title()
        prop_url = page.url
        print(f"   Título: {prop_title}")
        print(f"   URL: {prop_url}")
        await page.screenshot(path=str(screenshots / "05_property.png"))

        # Try finding stats section
        print("\n5. Buscando sección de estadísticas...")
        stats_selectors = [
            '.stats-container',
            '[class*="stat"]',
            '[class*="metric"]',
            '.detail-info',
            '.comment-owner',
            '#stats',
            '.ad-stats',
        ]
        for sel in stats_selectors:
            els = await page.query_selector_all(sel)
            if els:
                print(f"   ✓ Encontrado: {sel} ({len(els)} elementos)")
                for el in els[:3]:
                    text = await el.inner_text()
                    text_short = text[:120].replace("\n", " | ")
                    print(f"     → {text_short}")

        # Dump all visible text that could be stats
        all_text = await page.inner_text("body")
        keywords = ["visitas", "contactos", "favorito", "teléfono", "email", "guardado",
                     "estadísticas", "visits", "contacts", "favorites"]
        print("\n6. Búsqueda de texto relevante en la página:")
        for line in all_text.split("\n"):
            line_clean = line.strip().lower()
            if any(kw in line_clean for kw in keywords):
                print(f"   → {line.strip()[:150]}")

        # Save full HTML for offline analysis
        html = await page.content()
        html_path = screenshots / "property_page.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"\n   HTML completo guardado: {html_path}")

        print("\n   Esperando 10s para inspección visual...")
        await asyncio.sleep(10)

        await browser.close()

    print("\n✓ IDEALISTA: Test completado")
    print(f"  Screenshots guardados en: {screenshots}")


if __name__ == "__main__":
    asyncio.run(main())
