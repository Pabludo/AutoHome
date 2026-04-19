"""Clientify API endpoint discovery — probe available endpoints."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autohome.connectors.clientify import ClientifyConnector


ENDPOINTS_TO_TEST = [
    # Core endpoints from API docs
    ("GET", "/contacts/?page_size=2"),
    ("GET", "/companies/?page_size=2"),
    ("GET", "/deals/?page_size=2"),
    ("GET", "/tasks/?page_size=2"),
    ("GET", "/campaigns/?page_size=2"),
    ("GET", "/calls/?page_size=2"),
    ("GET", "/wall-entries/?page_size=2"),
    ("GET", "/users/"),
    ("GET", "/settings/"),
    # Real estate module
    ("GET", "/real-estate/?page_size=2"),
    ("GET", "/real-estate/properties/?page_size=2"),
    ("GET", "/properties/?page_size=2"),
    # Automations
    ("GET", "/automations/?page_size=2"),
    ("GET", "/automation-rules/?page_size=2"),
    # Webhooks
    ("GET", "/webhooks/"),
    # Products
    ("GET", "/products/?page_size=2"),
    # Pipelines (different paths)
    ("GET", "/pipelines/"),
    ("GET", "/deals/pipelines/"),
    ("GET", "/pipeline/"),
    ("GET", "/deal-stages/"),
    ("GET", "/stages/"),
    # Budgets
    ("GET", "/budgets/?page_size=2"),
    # Orders
    ("GET", "/orders/?page_size=2"),
    # Custom fields
    ("GET", "/custom-fields/"),
    ("GET", "/contact-custom-fields/"),
    # Tags
    ("GET", "/tags/"),
    # Sources
    ("GET", "/sources/"),
]


async def main():
    print("=== CLIENTIFY ENDPOINT DISCOVERY ===\n")

    async with ClientifyConnector() as client:
        print(f"Token: {client.token[:12]}...\n")

        working = []
        for method, path in ENDPOINTS_TO_TEST:
            try:
                if method == "GET":
                    resp = await client._client.get(path)
                status = resp.status_code
                if status == 200:
                    marker = "✓"
                    data = resp.json()
                    if isinstance(data, dict):
                        count = data.get("count", data.get("total", "?"))
                        keys = list(data.keys())[:6]
                    elif isinstance(data, list):
                        count = len(data)
                        keys = list(data[0].keys())[:6] if data else []
                    else:
                        count = "?"
                        keys = []
                    info = f"count={count}, keys={keys}"
                    working.append((path, data))
                elif status == 404:
                    marker = "✗"
                    info = "Not Found"
                elif status == 403:
                    marker = "⚠"
                    info = "Forbidden (exists but no permission)"
                else:
                    marker = "?"
                    info = f"Status {status}"

                print(f"  {marker} {method} {path:45s} → {info}")

            except Exception as e:
                print(f"  ✗ {method} {path:45s} → ERROR: {e}")

        # Print full data from working endpoints
        print("\n\n=== DETAILED DATA FROM WORKING ENDPOINTS ===\n")
        for path, data in working:
            print(f"\n--- {path} ---")
            text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            lines = text.split("\n")
            if len(lines) > 60:
                text = "\n".join(lines[:60]) + f"\n... ({len(lines)-60} more lines)"
            print(text)


if __name__ == "__main__":
    asyncio.run(main())
