"""End-to-end test: Inmovilla → Idealista stats scrape.

1. Fetch property 28751504 from Inmovilla to get Idealista ref
2. Navigate to Idealista URL with Playwright
3. Scrape the "Estadísticas" card and print results
"""

import asyncio

from rich.console import Console
from rich.panel import Panel

from autohome.connectors.idealista import IdealistaConnector
from autohome.connectors.inmovilla import InmovillaConnector

console = Console()
COD_OFER = "28751504"


async def main():
    # ── Step 1: Get Idealista URL from Inmovilla ──
    console.rule("[bold blue]Step 1 — Inmovilla: obtener URL de Idealista")
    async with InmovillaConnector() as imv:
        # Try extrainfo first for publication_url
        extra = await imv.get_property_extra_info(COD_OFER)
        publish = extra.get("publishinfo", [])

        idealista_url = None

        # Check publishinfo (can be list or dict)
        if isinstance(publish, dict) and "idealista" in publish:
            idealista_url = publish["idealista"].get("publication_url")
        elif isinstance(publish, list):
            for item in publish:
                if isinstance(item, dict) and "idealista" in item:
                    idealista_url = item["idealista"].get("publication_url")
                    break

        if idealista_url:
            console.print(f"  [green]URL desde publishinfo: {idealista_url}[/green]")
        else:
            # Fallback: get referenciacol from property details
            console.print("  publishinfo vacío, buscando referenciacol...")
            prop = await imv.get_property(COD_OFER)
            ref_col = prop.get("referenciacol", "")
            if ref_col:
                idealista_url = f"https://www.idealista.com/inmueble/{ref_col}/"
                console.print(f"  [green]URL construida desde referenciacol: {idealista_url}[/green]")
            else:
                console.print("[red]No se encontró referencia de Idealista[/red]")
                return

    # ── Step 2: Scrape Idealista stats ──
    console.rule("[bold blue]Step 2 — Idealista: login + scrape estadísticas")

    # Use Playwright directly for better control and debugging
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
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

    try:
        page = await context.new_page()

        # Go to login page
        console.print("  Navigando a login...")
        await page.goto("https://www.idealista.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # Screenshot: what does the login page look like?
        await page.screenshot(path="debug_01_login_page.png")
        console.print("  [dim]Screenshot: debug_01_login_page.png[/dim]")

        # Accept cookies if present
        try:
            accept = page.locator('#didomi-notice-agree-button')
            if await accept.is_visible(timeout=5000):
                await accept.click()
                await asyncio.sleep(2)
                console.print("  Cookies aceptadas")
        except Exception:
            console.print("  [dim]No cookie banner[/dim]")

        await page.screenshot(path="debug_02_after_cookies.png")

        # Try to find email input
        console.print("  Buscando campo email...")
        email_sel = 'input[name="email"], input[type="email"], #email, input[id*="email"]'
        try:
            await page.wait_for_selector(email_sel, timeout=10000)
            console.print("[green]  ✓ Campo email encontrado[/green]")
        except Exception:
            console.print("[yellow]  ✗ Campo email no encontrado[/yellow]")
            # Dump what inputs exist
            inputs = await page.query_selector_all("input")
            for inp in inputs:
                name = await inp.get_attribute("name") or ""
                typ = await inp.get_attribute("type") or ""
                iid = await inp.get_attribute("id") or ""
                console.print(f"    input: name={name} type={typ} id={iid}")
            await page.screenshot(path="debug_03_no_email.png")
            console.print("  [dim]Screenshot: debug_03_no_email.png[/dim]")

        # Fill email
        from autohome.config import get_settings
        settings = get_settings()
        await page.fill(email_sel, settings.idealista_email)
        await asyncio.sleep(1)

        # Click Continuar
        await page.click('button:has-text("Continuar")')
        await asyncio.sleep(3)
        await page.screenshot(path="debug_04_after_continuar.png")

        # Fill password
        try:
            await page.wait_for_selector('input[type="password"]', timeout=10000)
            await page.fill('input[type="password"]', settings.idealista_password)
            await asyncio.sleep(1)
            await page.click('button:has-text("Iniciar sesión")')
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(3)
            console.print("[green]  ✓ Login completado[/green]")
        except Exception as e:
            console.print(f"[yellow]  Login issue: {e}[/yellow]")

        await page.screenshot(path="debug_05_after_login.png")
        console.print(f"  URL actual: {page.url}")

        # ── Step 3: Navigate to property and scrape stats ──
        console.rule("[bold blue]Step 3 — Scrape estadísticas")
        console.print(f"  Navegando a {idealista_url} ...")
        await page.goto(idealista_url, wait_until="networkidle")
        await asyncio.sleep(3)
        await page.screenshot(path="debug_06_property_page.png")
        console.print(f"  URL: {page.url}")
        console.print(f"  Title: {await page.title()}")

        # Look for stats section — scroll to it to trigger lazy loading
        console.print("  Haciendo scroll hasta div#stats...")
        stats_div = await page.query_selector("div#stats")
        if stats_div:
            await stats_div.scroll_into_view_if_needed()
            await asyncio.sleep(3)
            console.print("[green]  ✓ div#stats encontrado y en viewport[/green]")
        else:
            # Try scrolling down in chunks to find it
            for i in range(10):
                await page.evaluate(f"window.scrollTo(0, {(i + 1) * 800})")
                await asyncio.sleep(1)
                stats_div = await page.query_selector("div#stats")
                if stats_div:
                    await stats_div.scroll_into_view_if_needed()
                    await asyncio.sleep(3)
                    console.print(f"[green]  ✓ div#stats encontrado tras scroll {i + 1}[/green]")
                    break
            else:
                console.print("[yellow]  ✗ div#stats NO encontrado tras scroll[/yellow]")

        # Wait for stats-ondemand content to load
        console.print("  Esperando contenido de stats-ondemand...")
        try:
            await page.wait_for_selector("div#stats-ondemand li", timeout=10000)
            console.print("[green]  ✓ Contenido cargado[/green]")
        except Exception:
            console.print("[yellow]  ✗ Timeout esperando li dentro de stats-ondemand[/yellow]")
            # Take screenshot for debug
            await page.screenshot(path="debug_07_stats_area.png")
            console.print("  [dim]Screenshot: debug_07_stats_area.png[/dim]")

        stats_od = await page.query_selector("div#stats-ondemand")
        if stats_od:
            console.print("[green]  ✓ div#stats-ondemand encontrado[/green]")
            html = await stats_od.inner_html()
            console.print(f"  Raw HTML:\n{html}")

            # Parse items
            items = await stats_od.query_selector_all("li")
            console.print()
            results = {}
            for item in items:
                strong = await item.query_selector("strong")
                span = await item.query_selector("span")
                num = (await strong.text_content()).strip() if strong else "?"
                label = (await span.text_content()).strip() if span else "?"
                console.print(f"  [bold]{num}[/bold] {label}")
                results[label] = num

            # Also get the "Anuncio actualizado" text
            updated_p = await stats_od.query_selector("p")
            if updated_p:
                updated_text = await updated_p.text_content()
                console.print(f"\n  [dim]{updated_text.strip()}[/dim]")

            console.rule("[bold green]Resultado final")
            console.print(Panel.fit(
                "\n".join(f"[bold]{v}[/bold] {k}" for k, v in results.items()),
                title="Estadísticas Idealista — Propiedad " + COD_OFER,
            ))
        else:
            console.print("[red]  ✗ div#stats-ondemand NO encontrado[/red]")
            await page.screenshot(path="debug_07_no_stats.png")
            console.print("  [dim]Screenshot: debug_07_no_stats.png[/dim]")

    finally:
        await context.close()
        await browser.close()
        await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
