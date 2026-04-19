"""Inmovilla CRM API connector."""

import httpx

from autohome.config import get_settings


class InmovillaConnector:
    """Async client for Inmovilla REST API."""

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.inmovilla_api_url.rstrip("/")
        self._token = settings.inmovilla_api_token
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        if not self._base_url:
            msg = "INMOVILLA_API_URL not configured in .env"
            raise ValueError(msg)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def check_connection(self) -> bool:
        """Verify API is reachable."""
        resp = await self._client.get("/properties/?limit=1")
        return resp.status_code == 200

    async def list_prospects(self, status: str = "active") -> list[dict]:
        """Fetch prospects filtered by status."""
        resp = await self._client.get("/prospects/", params={"status": status})
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def get_prospect(self, prospect_id: str) -> dict:
        """Fetch a single prospect with full details."""
        resp = await self._client.get(f"/prospects/{prospect_id}/")
        resp.raise_for_status()
        return resp.json()

    async def list_properties(self) -> list[dict]:
        """Fetch properties list."""
        resp = await self._client.get("/properties/")
        resp.raise_for_status()
        return resp.json().get("results", [])
