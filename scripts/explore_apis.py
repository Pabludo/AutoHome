"""
AutoHome — API Exploration Script
==================================
Tests connectivity and data reading from all three platforms:
1. Clientify (REST API — auto-auth with user/password)
2. Inmovilla (REST API — requires token from dashboard)
3. Idealista (Playwright scraping)

Run: python scripts/explore_apis.py
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_json(data: dict | list, max_lines: int = 40):
    """Pretty-print JSON data, truncated if needed."""
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    lines = text.split("\n")
    if len(lines) > max_lines:
        text = "\n".join(lines[:max_lines]) + f"\n  ... ({len(lines) - max_lines} more lines)"
    console.print(text)


# ============================================================================
# 1. CLIENTIFY
# ============================================================================
async def explore_clientify():
    """Test Clientify API: auth + read contacts, deals, pipelines."""
    console.print(Panel("[bold cyan]1. CLIENTIFY — API REST[/bold cyan]", expand=False))

    from autohome.connectors.clientify import ClientifyConnector

    try:
        async with ClientifyConnector() as client:
            # Auth
            console.print("[green]✓[/green] Token obtenido automáticamente via user/password")
            console.print(f"  Token: {client.token[:12]}...{client.token[-4:]}")

            # Connection check
            ok = await client.check_connection()
            console.print(f"  Connection check: {'[green]OK[/green]' if ok else '[red]FAIL[/red]'}")

            # Contacts
            console.print("\n[bold]— Contactos —[/bold]")
            contacts = await client.list_contacts(page_size=5)
            count = contacts.get("count", 0)
            console.print(f"  Total contactos: [yellow]{count}[/yellow]")
            for c in contacts.get("results", [])[:5]:
                name = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
                email = c.get("email", "—")
                console.print(f"  · {name} ({email})")

            # Deals
            console.print("\n[bold]— Deals (Oportunidades) —[/bold]")
            deals = await client.list_deals(page_size=5)
            deal_count = deals.get("count", 0)
            console.print(f"  Total deals: [yellow]{deal_count}[/yellow]")
            for d in deals.get("results", [])[:5]:
                name = d.get("name", "—")
                amount = d.get("amount", 0)
                status = d.get("status_display", d.get("status", "—"))
                console.print(f"  · {name} — {amount}€ — {status}")

            # Pipelines
            console.print("\n[bold]— Pipelines —[/bold]")
            pipelines = await client.list_pipelines()
            console.print(f"  Total pipelines: [yellow]{len(pipelines)}[/yellow]")
            for p in pipelines:
                console.print(f"  · {p.get('name', '—')} (id={p.get('id')})")

            # Companies
            console.print("\n[bold]— Empresas —[/bold]")
            companies = await client.list_companies(page_size=5)
            comp_count = companies.get("count", 0)
            console.print(f"  Total empresas: [yellow]{comp_count}[/yellow]")
            for co in companies.get("results", [])[:3]:
                console.print(f"  · {co.get('name', '—')}")

            console.print("\n[green bold]✓ CLIENTIFY: CONEXIÓN EXITOSA[/green bold]")
            return True

    except Exception as e:
        console.print(f"[red bold]✗ CLIENTIFY ERROR: {e}[/red bold]")
        return False


# ============================================================================
# 2. INMOVILLA
# ============================================================================
async def explore_inmovilla():
    """Test Inmovilla API: list properties, get extra info, leads."""
    console.print(Panel("[bold cyan]2. INMOVILLA — API REST[/bold cyan]", expand=False))

    from autohome.config import get_settings
    settings = get_settings()

    if not settings.inmovilla_api_token:
        console.print("[yellow]⚠ INMOVILLA_API_TOKEN no configurado en .env[/yellow]")
        console.print("  Para generar el token:")
        console.print("  1. Entra en Inmovilla → Ajustes → Configuración → Opciones")
        console.print("  2. Busca 'Token para API REST' → Crear Token")
        console.print("  3. Copia el token y pégalo en .env como INMOVILLA_API_TOKEN=xxxxx")
        console.print("  Docs: https://procesos.apinmo.com/api/v1/apidoc/")
        console.print("\n[yellow bold]⏸ INMOVILLA: PENDIENTE TOKEN[/yellow bold]")
        return None

    from autohome.connectors.inmovilla import InmovillaConnector

    try:
        async with InmovillaConnector() as client:
            # Connection check
            ok = await client.check_connection()
            console.print(f"  Connection check: {'[green]OK[/green]' if ok else '[red]FAIL[/red]'}")

            # List properties
            console.print("\n[bold]— Listado de Propiedades/Prospectos —[/bold]")
            properties = await client.list_properties()
            console.print(f"  Total propiedades: [yellow]{len(properties)}[/yellow]")

            # Show first 5
            for prop in properties[:5]:
                ref = prop.get("ref", "—")
                cod = prop.get("cod_ofer", "—")
                prospecto = "🔵 Prospecto" if prop.get("prospecto") else "🏠 Propiedad"
                disp = "Activo" if not prop.get("nodisponible") else "No disponible"
                console.print(f"  · [{ref}] cod_ofer={cod} — {prospecto} — {disp}")

            # Extra info for first property (Idealista URL + leads)
            if properties:
                first_cod = str(properties[0].get("cod_ofer", ""))
                if first_cod:
                    console.print(f"\n[bold]— Extra Info (cod_ofer={first_cod}) —[/bold]")
                    try:
                        extra = await client.get_property_extra_info(first_cod)
                        print_json(extra)
                    except Exception as e:
                        console.print(f"  [yellow]Extra info no disponible: {e}[/yellow]")

            # Recent leads
            console.print("\n[bold]— Leads Recientes (últimos 30 días) —[/bold]")
            try:
                end = datetime.now().strftime("%Y-%m-%d")
                start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                leads = await client.get_leads(start, end)
                lead_list = leads if isinstance(leads, list) else leads.get("leads", [])
                console.print(f"  Leads encontrados: [yellow]{len(lead_list)}[/yellow]")
                for lead in lead_list[:3]:
                    source = lead.get("source", "—")
                    name = f"{lead.get('contact_firstname', '')} {lead.get('contact_lastname', '')}".strip()
                    date = lead.get("date", "—")
                    console.print(f"  · {date} — {name} — via {source}")
            except Exception as e:
                console.print(f"  [yellow]Leads no disponible: {e}[/yellow]")

            console.print("\n[green bold]✓ INMOVILLA: CONEXIÓN EXITOSA[/green bold]")
            return True

    except Exception as e:
        console.print(f"[red bold]✗ INMOVILLA ERROR: {e}[/red bold]")
        return False


# ============================================================================
# 3. IDEALISTA
# ============================================================================
async def explore_idealista():
    """Test Idealista scraping: login + navigate to a property page."""
    console.print(Panel("[bold cyan]3. IDEALISTA — Scraping (Playwright)[/bold cyan]", expand=False))

    from autohome.config import get_settings
    settings = get_settings()

    if not settings.idealista_email or not settings.idealista_password:
        console.print("[yellow]⚠ Credenciales de Idealista no configuradas[/yellow]")
        return None

    from playwright.async_api import async_playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Visible for debugging
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

            # Step 1: Navigate to login
            console.print("  Navegando a idealista.com/login...")
            await page.goto("https://www.idealista.com", wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Check if blocked by Cloudflare / CAPTCHA
            title = await page.title()
            content = await page.content()
            console.print(f"  Título de página: {title}")

            if "challenge" in content.lower() or "captcha" in content.lower():
                console.print("[yellow]⚠ Detectado anti-bot (Cloudflare/CAPTCHA)[/yellow]")
                console.print("  Esto es esperado. Opciones:")
                console.print("  1. Usar modo headful con navegador real")
                console.print("  2. Importar cookies de sesión autenticada")
                console.print("  3. Usar proxy residencial")

            # Take screenshot for debugging
            screenshots_dir = Path(__file__).parent.parent / "data" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshots_dir / "idealista_landing.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)
            console.print(f"  Screenshot guardado: {screenshot_path}")

            # Step 2: Try navigating to login page
            console.print("  Intentando login...")
            try:
                await page.goto("https://www.idealista.com/login", wait_until="domcontentloaded")
                await asyncio.sleep(3)

                login_title = await page.title()
                console.print(f"  Título login: {login_title}")

                screenshot_login = screenshots_dir / "idealista_login.png"
                await page.screenshot(path=str(screenshot_login), full_page=False)
                console.print(f"  Screenshot login: {screenshot_login}")

                # Try to find email input
                email_input = await page.query_selector('input[name="email"], input[type="email"], #email')
                if email_input:
                    console.print("[green]  ✓ Campo de email encontrado[/green]")
                    await email_input.fill(settings.idealista_email)
                    await asyncio.sleep(1)

                    # Find password
                    pwd_input = await page.query_selector('input[name="password"], input[type="password"], #password')
                    if pwd_input:
                        console.print("[green]  ✓ Campo de password encontrado[/green]")
                        await pwd_input.fill(settings.idealista_password)
                        await asyncio.sleep(1)

                        # Find submit
                        submit = await page.query_selector('button[type="submit"], input[type="submit"]')
                        if submit:
                            console.print("  Haciendo click en login...")
                            await submit.click()
                            await asyncio.sleep(5)

                            post_login_title = await page.title()
                            console.print(f"  Título post-login: {post_login_title}")

                            screenshot_post = screenshots_dir / "idealista_post_login.png"
                            await page.screenshot(path=str(screenshot_post), full_page=False)
                            console.print(f"  Screenshot post-login: {screenshot_post}")

                            # Check if logged in
                            logged_in = await page.query_selector(
                                '[class*="user-menu"], [class*="logged"], .icon-user-logged'
                            )
                            if logged_in:
                                console.print("[green bold]  ✓ LOGIN EXITOSO[/green bold]")
                            else:
                                console.print("[yellow]  ⚠ Login enviado pero no se ha confirmado la sesión[/yellow]")
                                console.print("  Posible CAPTCHA, 2FA, o cambio en la UI")
                else:
                    console.print("[yellow]  ⚠ No se encontró campo de email en la página[/yellow]")
                    console.print("  Posible bloqueo anti-bot previo al formulario")

            except Exception as e:
                console.print(f"  [yellow]Error en proceso de login: {e}[/yellow]")

            # Step 3: Try navigating to a public property page (no auth needed)
            console.print("\n[bold]— Test: Página pública de inmueble —[/bold]")
            try:
                test_url = "https://www.idealista.com/inmueble/111029821/"
                console.print(f"  Navegando a: {test_url}")
                await page.goto(test_url, wait_until="domcontentloaded")
                await asyncio.sleep(3)

                prop_title = await page.title()
                console.print(f"  Título: {prop_title}")

                screenshot_prop = screenshots_dir / "idealista_property.png"
                await page.screenshot(path=str(screenshot_prop), full_page=False)
                console.print(f"  Screenshot propiedad: {screenshot_prop}")

                # Try to extract basic info visible on the page
                price_el = await page.query_selector('.info-data-price, [class*="price"]')
                if price_el:
                    price_text = await price_el.inner_text()
                    console.print(f"  [green]Precio encontrado: {price_text}[/green]")

            except Exception as e:
                console.print(f"  [yellow]Error navegando propiedad: {e}[/yellow]")

            await browser.close()

        console.print("\n[green bold]✓ IDEALISTA: EXPLORACIÓN COMPLETADA[/green bold]")
        console.print("  (Ver screenshots en data/screenshots/ para análisis visual)")
        return True

    except Exception as e:
        console.print(f"[red bold]✗ IDEALISTA ERROR: {e}[/red bold]")
        return False


# ============================================================================
# MAIN
# ============================================================================
async def main():
    console.print(Panel(
        "[bold white]AutoHome — Exploración de APIs y Plataformas[/bold white]\n"
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        title="🏠 AutoHome",
        expand=False,
    ))

    results = {}

    # 1. Clientify
    results["clientify"] = await explore_clientify()
    console.print()

    # 2. Inmovilla
    results["inmovilla"] = await explore_inmovilla()
    console.print()

    # 3. Idealista (last because it opens a browser)
    results["idealista"] = await explore_idealista()
    console.print()

    # Summary
    console.print(Panel("[bold]RESUMEN DE EXPLORACIÓN[/bold]", expand=False))
    table = Table()
    table.add_column("Plataforma", style="bold")
    table.add_column("Estado")
    table.add_column("Notas")

    for name, result in results.items():
        if result is True:
            status = "[green]✓ Conectado[/green]"
            notes = "API accesible y datos disponibles"
        elif result is False:
            status = "[red]✗ Error[/red]"
            notes = "Revisar credenciales o configuración"
        else:
            status = "[yellow]⏸ Pendiente[/yellow]"
            notes = "Requiere configuración adicional"
        table.add_row(name.upper(), status, notes)

    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
