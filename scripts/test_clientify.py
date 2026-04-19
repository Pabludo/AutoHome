"""Quick Clientify-only connectivity test."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autohome.connectors.clientify import ClientifyConnector


async def main():
    print("=== CLIENTIFY TEST ===")
    try:
        async with ClientifyConnector() as client:
            print(f"✓ Token obtenido: {client.token[:12]}...{client.token[-4:]}")

            ok = await client.check_connection()
            print(f"✓ Conexión: {'OK' if ok else 'FAIL'}")

            contacts = await client.list_contacts(page_size=3)
            print(f"\nContactos total: {contacts.get('count', 0)}")
            for c in contacts.get("results", [])[:3]:
                name = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
                email = c.get("email", "—")
                print(f"  · {name} <{email}>")

            deals = await client.list_deals(page_size=3)
            print(f"\nDeals total: {deals.get('count', 0)}")
            for d in deals.get("results", [])[:3]:
                print(f"  · {d.get('name', '—')} — {d.get('amount', 0)}€")

            pipelines = await client.list_pipelines()
            print(f"\nPipelines: {len(pipelines)}")
            for p in pipelines:
                print(f"  · {p.get('name', '—')} (id={p.get('id')})")

            companies = await client.list_companies(page_size=3)
            print(f"\nEmpresas total: {companies.get('count', 0)}")
            for co in companies.get("results", [])[:3]:
                print(f"  · {co.get('name', '—')}")

            # Full first contact JSON for analysis
            results = contacts.get("results", [])
            if results:
                print("\n=== ESTRUCTURA DE CONTACTO (primer registro) ===")
                print(json.dumps(results[0], indent=2, ensure_ascii=False, default=str))

            # Full first deal JSON
            deal_results = deals.get("results", [])
            if deal_results:
                print("\n=== ESTRUCTURA DE DEAL (primer registro) ===")
                print(json.dumps(deal_results[0], indent=2, ensure_ascii=False, default=str))

            print("\n✓ CLIENTIFY: TODO OK")

    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
