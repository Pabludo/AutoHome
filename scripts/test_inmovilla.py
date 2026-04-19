"""Test Inmovilla API connection and explore available data."""

import asyncio

from rich.console import Console
from rich.table import Table

from autohome.connectors.inmovilla import InmovillaConnector

console = Console()


async def main():
    console.rule("[bold blue]Inmovilla API Test")

    async with InmovillaConnector() as imv:
        # 1. Connection check
        console.print("\n[bold]1. Connection check...[/bold]")
        ok = await imv.check_connection()
        if ok:
            console.print("[green]✓ Token válido — conexión OK[/green]")
        else:
            console.print("[red]✗ Token inválido o error de conexión[/red]")
            return

        # 2. List properties
        console.print("\n[bold]2. Listado de propiedades...[/bold]")
        try:
            props = await imv.list_properties()
            console.print(f"  → {len(props)} propiedades encontradas")

            if props:
                table = Table(title="Primeras 10 propiedades")
                # Infer columns from first item
                sample = props[0]
                for key in list(sample.keys())[:8]:
                    table.add_column(str(key), overflow="fold")

                for p in props[:10]:
                    row = [str(p.get(k, "")) for k in list(sample.keys())[:8]]
                    table.add_row(*row)

                console.print(table)
                console.print(f"\n[dim]Claves disponibles: {list(sample.keys())}[/dim]")

                # 3. Try extrainfo on first property
                first_id = props[0].get("cod_ofer") or props[0].get("id") or props[0].get("referencia")
                if first_id:
                    console.print(f"\n[bold]3. Extra info para propiedad {first_id} (prospecto=True)...[/bold]")
                    try:
                        extra = await imv.get_property_extra_info(str(first_id))
                        pub = extra.get("publishinfo", [])
                        leads_e = extra.get("leads", [])
                        console.print(f"  publishinfo: {pub}")
                        console.print(f"  leads: {leads_e}")
                        raw = str(extra)
                        if "idealista" in raw.lower():
                            console.print("[green]  ✓ Contiene referencia a Idealista![/green]")
                    except Exception as e:
                        console.print(f"[yellow]  Extra info error: {e}[/yellow]")

        except Exception as e:
            console.print(f"[red]Error listando propiedades: {e}[/red]")

        # 3b. Try extrainfo on a non-prospecto (published property)
        published = [p for p in props if not p.get("prospecto")][:3]
        if published:
            console.print("\n[bold]3b. Extra info de propiedades publicadas (prospecto=False)...[/bold]")
            for p in published:
                pid = str(p["cod_ofer"])
                try:
                    extra = await imv.get_property_extra_info(pid)
                    pub = extra.get("publishinfo", [])
                    leads_e = extra.get("leads", [])
                    console.print(f"  [{pid}] publishinfo: {pub}")
                    console.print(f"  [{pid}] leads: {leads_e}")
                    if pub:
                        break
                except Exception as e:
                    console.print(f"  [{pid}] error: {e}")

        # 4. List leads by date
        console.print("\n[bold]4. Leads recientes (últimos 30 días)...[/bold]")
        try:
            leads = await imv.get_leads("2026-03-01", "2026-04-19")
            if isinstance(leads, list):
                console.print(f"  → {len(leads)} leads")
                if leads:
                    console.print(f"  Claves: {list(leads[0].keys())}")
                    for lead in leads[:3]:
                        console.print(f"  - {lead}")
            else:
                console.print(f"  Respuesta: {leads}")
        except Exception as e:
            console.print(f"[yellow]  Leads error: {e}[/yellow]")

        # 5. Owner info for first property
        console.print("\n[bold]5. Propietario de primera propiedad...[/bold]")
        try:
            first_cod = str(props[0]["cod_ofer"])
            owner = await imv.get_owner_by_property(first_cod)
            console.print(f"  Propietario: {owner}")
        except Exception as e:
            console.print(f"[yellow]  Owner error: {e}[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())
