"""CLI entry point for AutoHome."""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def main():
    """AutoHome - Real Estate Metrics Automation."""
    pass


@main.command()
def check_connections():
    """Test connectivity to all external services."""
    import asyncio

    asyncio.run(_check_all_connections())


async def _check_all_connections():
    """Run all connectivity checks."""
    table = Table(title="Connection Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    # Check Clientify
    status, details = await _check_clientify()
    table.add_row("Clientify API", status, details)

    # Check Inmovilla
    status, details = await _check_inmovilla()
    table.add_row("Inmovilla API", status, details)

    # Check Idealista (browser launch)
    status, details = await _check_idealista()
    table.add_row("Idealista (Playwright)", status, details)

    console.print(table)


async def _check_clientify() -> tuple[str, str]:
    """Test Clientify API connectivity."""
    try:
        from autohome.connectors.clientify import ClientifyConnector

        async with ClientifyConnector() as client:
            result = await client.check_connection()
            if result:
                return "[green]✓ Connected[/green]", "API token valid"
            return "[red]✗ Failed[/red]", "Invalid token or unreachable"
    except Exception as e:
        return "[red]✗ Error[/red]", str(e)


async def _check_inmovilla() -> tuple[str, str]:
    """Test Inmovilla API connectivity."""
    try:
        from autohome.connectors.inmovilla import InmovillaConnector

        async with InmovillaConnector() as client:
            result = await client.check_connection()
            if result:
                return "[green]✓ Connected[/green]", "API accessible"
            return "[red]✗ Failed[/red]", "Cannot reach API"
    except Exception as e:
        return "[yellow]⚠ Not configured[/yellow]", str(e)


async def _check_idealista() -> tuple[str, str]:
    """Test Playwright browser launch."""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.idealista.com", timeout=15000)
            title = await page.title()
            await browser.close()
            return "[green]✓ Browser OK[/green]", f"Page loaded: {title[:50]}"
    except Exception as e:
        return "[red]✗ Error[/red]", str(e)


@main.command()
def run_pipeline():
    """Execute the full pipeline once."""
    console.print("[bold]Running pipeline...[/bold]")
    console.print("[yellow]Not yet implemented. Coming in Phase 1.[/yellow]")


@main.command()
@click.argument("url")
def scrape_test(url: str):
    """Test scraping a single Idealista property URL."""
    import asyncio

    asyncio.run(_scrape_single(url))


async def _scrape_single(url: str):
    """Scrape a single Idealista property for testing."""
    try:
        from autohome.connectors.idealista import IdealistaConnector

        async with IdealistaConnector() as scraper:
            metrics = await scraper.scrape_property_stats(url)
            console.print_json(data=metrics)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
