"""Casafari API connector.

API docs: https://docs.api.casafari.com/
Base URL: https://api.casafari.com
Auth: POST /login → access_token (JWT), used as Bearer in subsequent calls.
      Tokens expire; use refresh_token via GET /refresh-token to renew.

Key endpoints used:
  POST /login                            → authenticate, get access_token
  GET  /refresh-token                    → renew access_token (Bearer refresh_token)
  POST /api/v1/properties/search         → search active/sold properties
  GET  /api/v1/properties/search/{id}    → property detail + price history
  POST /api/v1/comparables/search        → comparable properties + price estimate
  POST /api/v1/valuation/comparables-prices → fast_sell / fair_market / out_of_market
  POST /api/v1/references/locations      → resolve location names to IDs
"""

import httpx

from autohome.config import get_settings


class CasafariConnector:
    """Async client for Casafari REST API."""

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.casafari_base_url.rstrip("/")
        self._email = settings.casafari_email
        self._password = settings.casafari_password
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        if not self._email or not self._password:
            msg = (
                "CASAFARI_EMAIL and CASAFARI_PASSWORD must be set in .env. "
                "Use the same credentials as the Casafari web account."
            )
            raise ValueError(msg)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=30.0,
            follow_redirects=True,
        )
        await self._login()
        return self

    async def __aexit__(self, *_):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    async def _login(self) -> None:
        resp = await self._client.post(
            "/login",
            json={"email": self._email, "password": self._password},
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._refresh_token = data["refresh_token"]

    async def _refresh(self) -> None:
        """Use the refresh_token to obtain a new access_token."""
        resp = await self._client.get(
            "/refresh-token",
            headers={"Authorization": f"Bearer {self._refresh_token}"},
        )
        resp.raise_for_status()
        self._access_token = resp.json()["access_token"]

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def _get(self, path: str, **kwargs) -> dict:
        resp = await self._client.get(path, headers=self._auth_headers(), **kwargs)
        if resp.status_code == 401:
            await self._refresh()
            resp = await self._client.get(path, headers=self._auth_headers(), **kwargs)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, payload: dict, **kwargs) -> dict:
        resp = await self._client.post(
            path, json=payload, headers=self._auth_headers(), **kwargs
        )
        if resp.status_code == 401:
            await self._refresh()
            resp = await self._client.post(
                path, json=payload, headers=self._auth_headers(), **kwargs
            )
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    async def get_location_ids(self, name: str) -> list[dict]:
        """Resolve a location name to Casafari location objects.

        Returns a list of matching locations with ``location_id`` and ``name``.
        Use the ``location_id`` values in search/comparables calls.
        """
        data = await self._post("/api/v1/references/locations", {"name": name})
        return data.get("locations", [])

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    async def search_properties(
        self,
        search_operations: list[str],
        location_ids: list[int] | None = None,
        types: list[str] | None = None,
        price_from: int | None = None,
        price_to: int | None = None,
        bedrooms_from: int | None = None,
        bedrooms_to: int | None = None,
        total_area_from: int | None = None,
        total_area_to: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Search properties.

        ``search_operations``: one or more of "sale", "sold", "sale_hold",
        "rent", "rented", "rent_hold".

        Returns ``{"count": N, "next": url_or_null, "results": [...]}``.
        """
        payload: dict = {"search_operations": search_operations}
        if location_ids:
            payload["location_ids"] = location_ids
        if types:
            payload["types"] = types
        if price_from is not None:
            payload["price_from"] = price_from
        if price_to is not None:
            payload["price_to"] = price_to
        if bedrooms_from is not None:
            payload["bedrooms_from"] = bedrooms_from
        if bedrooms_to is not None:
            payload["bedrooms_to"] = bedrooms_to
        if total_area_from is not None:
            payload["total_area_from"] = total_area_from
        if total_area_to is not None:
            payload["total_area_to"] = total_area_to
        return await self._post(
            "/api/v1/properties/search",
            payload,
            params={"limit": limit, "offset": offset},
        )

    async def get_property(self, property_id: int | str) -> dict:
        """Get full property detail including price history and listings."""
        return await self._get(f"/api/v1/properties/search/{property_id}")

    # ------------------------------------------------------------------
    # Comparables & Valuation
    # ------------------------------------------------------------------

    async def search_comparables(
        self,
        operation: str,
        comparables_types: list[str],
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        comparables_count: int = 20,
        bedrooms: int | None = None,
        total_area: int | None = None,
        condition: str | None = None,
        sold_or_rented_after: str | None = None,
    ) -> dict:
        """Search comparable properties around a coordinate point.

        Returns ``results``, ``statistics``, and ``estimated_prices``
        (fast_sell_price, fair_market_price, out_of_market_price).
        """
        payload: dict = {
            "comparables_count": comparables_count,
            "operation": operation,
            "comparables_types": comparables_types,
            "location_boundary": {
                "circle": {
                    "target_point": {"coordinates": {"latitude": latitude, "longitude": longitude}},
                    "distance": radius_km,
                }
            },
        }
        if bedrooms is not None:
            payload["bedrooms"] = bedrooms
        if total_area is not None:
            payload["total_area"] = total_area
        if condition:
            payload["condition"] = condition
        if sold_or_rented_after:
            payload["sold_or_rented_after"] = sold_or_rented_after
        return await self._post("/api/v1/comparables/search", payload)

    async def get_valuation(
        self,
        operation: str,
        comparables_types: list[str],
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        comparables_count: int = 20,
        bedrooms: int | None = None,
        total_area: int | None = None,
        condition: str | None = None,
    ) -> dict:
        """Get estimated prices for a property.

        Returns ``statistics`` and ``estimated_prices``
        (fast_sell_price, fair_market_price, out_of_market_price).
        """
        payload: dict = {
            "comparables_count": comparables_count,
            "operation": operation,
            "comparables_types": comparables_types,
            "location_boundary": {
                "circle": {
                    "target_point": {"coordinates": {"latitude": latitude, "longitude": longitude}},
                    "distance": radius_km,
                }
            },
        }
        if bedrooms is not None:
            payload["bedrooms"] = bedrooms
        if total_area is not None:
            payload["total_area"] = total_area
        if condition:
            payload["condition"] = condition
        return await self._post("/api/v1/valuation/comparables-prices", payload)

    # ------------------------------------------------------------------
    # Listing alerts
    # ------------------------------------------------------------------

    async def get_alert_feeds(self) -> list[dict]:
        """Return all alert feeds configured for the authenticated user."""
        return await self._get("/api/v1/listing-alerts/feeds")
