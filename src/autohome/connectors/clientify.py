"""Clientify CRM API connector."""

import httpx

from autohome.config import get_settings


class ClientifyConnector:
    """Async client for Clientify REST API."""

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.clientify_base_url.rstrip("/")
        self._token = settings.clientify_api_token
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Token {self._token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def check_connection(self) -> bool:
        """Verify API token is valid by fetching contacts list."""
        resp = await self._client.get("/contacts/?page_size=1")
        return resp.status_code == 200

    async def find_contact_by_email(self, email: str) -> dict | None:
        """Search for a contact by email address."""
        resp = await self._client.get("/contacts/", params={"query": email})
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            return results[0] if results else None
        return None

    async def create_deal(self, deal_data: dict) -> dict:
        """Create a new deal in Clientify."""
        resp = await self._client.post("/deals/", json=deal_data)
        resp.raise_for_status()
        return resp.json()

    async def update_deal(self, deal_id: int, deal_data: dict) -> dict:
        """Update an existing deal."""
        resp = await self._client.patch(f"/deals/{deal_id}/", json=deal_data)
        resp.raise_for_status()
        return resp.json()

    async def add_note(self, contact_id: int, content: str) -> dict:
        """Add a note to a contact."""
        resp = await self._client.post(
            f"/contacts/{contact_id}/notes/",
            json={"content": content},
        )
        resp.raise_for_status()
        return resp.json()

    async def list_pipelines(self) -> list[dict]:
        """List available pipelines."""
        resp = await self._client.get("/pipelines/")
        resp.raise_for_status()
        return resp.json().get("results", [])
