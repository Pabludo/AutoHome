"""Clientify CRM API connector."""

import httpx

from autohome.config import get_settings


class ClientifyConnector:
    """Async client for Clientify REST API.

    Supports both token auth and username/password auth (obtains token automatically).
    """

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.clientify_base_url.rstrip("/")
        self._token = settings.clientify_api_token
        self._username = settings.clientify_username
        self._password = settings.clientify_password
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=30.0,
        )
        # If no token provided, obtain one via username/password
        if not self._token and self._username and self._password:
            await self._obtain_token()
        self._client.headers.update({
            "Authorization": f"Token {self._token}",
            "Content-Type": "application/json",
        })
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def _obtain_token(self) -> str:
        """Authenticate with username/password to get API token."""
        resp = await self._client.post(
            "/api-auth/obtain_token/",
            json={"username": self._username, "password": self._password},
        )
        resp.raise_for_status()
        self._token = resp.json()["token"]
        return self._token

    @property
    def token(self) -> str:
        return self._token

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

    async def list_contacts(self, page_size: int = 10) -> dict:
        """List contacts with pagination info."""
        resp = await self._client.get("/contacts/", params={"page_size": page_size})
        resp.raise_for_status()
        return resp.json()

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

    async def list_deals(self, page_size: int = 10) -> dict:
        """List deals with pagination."""
        resp = await self._client.get("/deals/", params={"page_size": page_size})
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
        resp = await self._client.get("/deals/pipelines/")
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def list_companies(self, page_size: int = 10) -> dict:
        """List companies."""
        resp = await self._client.get("/companies/", params={"page_size": page_size})
        resp.raise_for_status()
        return resp.json()
