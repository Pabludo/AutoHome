"""Inmovilla CRM API connector.

API docs: https://procesos.apinmo.com/api/v1/apidoc/
Base URL: https://procesos.inmovilla.com/api/v1
Auth: Header 'Token: {token}' (generated from Ajustes → Opciones)
Rate limits: clientes 20/min, propiedades 10/min, enums 2/min

Real data shapes discovered during testing:

listado → list[dict] with keys:
    cod_ofer, ref, nodisponible, prospecto, fechaact

property detail → dict with 100+ fields including:
    cod_ofer, ref, precio, precioinmo, m_cons, habitaciones,
    banyos, latitud, longitud, referenciacol (= Idealista ref),
    keycli (owner id), ...

extrainfo → dict with keys:
    publishinfo (list of dicts per portal), leads (list)
    publishinfo entry: {"idealista": {"state", "message",
        "alerts_number", "quality_percentage", "publication_url"}}

propietarios → dict with keys:
    cod_cli, nombre, apellidos, email, telefono1, telefono2,
    propiedades (list of {cod_ofer, ref, panel, estadistica, disponible})
"""

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
        if not self._token:
            msg = (
                "INMOVILLA_API_TOKEN not configured. "
                "Generate from Inmovilla: Ajustes → Opciones"
                " → Token para API REST"
            )
            raise ValueError(msg)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Token": self._token,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def check_connection(self) -> bool:
        """Verify API token is valid by listing properties."""
        resp = await self._client.get("/propiedades/?listado")
        return resp.status_code == 200

    # --- Properties ---

    async def list_properties(self) -> list[dict]:
        """List all properties (ordered by update date).

        Each item has: cod_ofer, ref, nodisponible, prospecto, fechaact.
        """
        resp = await self._client.get("/propiedades/?listado")
        resp.raise_for_status()
        return resp.json()

    async def get_property(self, cod_ofer: str) -> dict:
        """Get full property details by cod_ofer (100+ fields)."""
        resp = await self._client.get(
            f"/propiedades/?cod_ofer={cod_ofer}",
        )
        resp.raise_for_status()
        return resp.json()

    async def get_property_extra_info(self, cod_ofer: str) -> dict:
        """Get portal publication status and leads for a property.

        Returns dict with ``publishinfo`` (list) and ``leads`` (list).
        """
        resp = await self._client.get(
            f"/propiedades/?extrainfo&cod_ofer={cod_ofer}",
        )
        resp.raise_for_status()
        return resp.json()

    async def get_idealista_url(self, cod_ofer: str) -> str | None:
        """Resolve the Idealista listing URL for a property.

        Strategy:
        1. Check ``publishinfo.idealista.publication_url`` from extrainfo.
        2. Fallback: build URL from ``referenciacol`` in property detail.
        """
        extra = await self.get_property_extra_info(cod_ofer)
        publish = extra.get("publishinfo", [])

        # publishinfo is a list; look for idealista entry
        if isinstance(publish, dict) and "idealista" in publish:
            url = publish["idealista"].get("publication_url")
            if url:
                return url
        elif isinstance(publish, list):
            for item in publish:
                if isinstance(item, dict) and "idealista" in item:
                    url = item["idealista"].get("publication_url")
                    if url:
                        return url

        # Fallback: referenciacol from property detail
        prop = await self.get_property(cod_ofer)
        ref_col = prop.get("referenciacol", "")
        if ref_col:
            return f"https://www.idealista.com/inmueble/{ref_col}/"
        return None

    # --- Owners ---

    async def get_owner_by_property(self, cod_ofer: str) -> dict:
        """Get property owner details by property code.

        Returns dict with: cod_cli, nombre, apellidos, email,
        telefono1, telefono2, propiedades (list), ...
        """
        resp = await self._client.get(
            f"/propietarios/?cod_ofer={cod_ofer}",
        )
        resp.raise_for_status()
        return resp.json()

    async def get_owner(self, cod_cli: str) -> dict:
        """Get property owner by client code."""
        resp = await self._client.get(
            f"/propietarios/?cod_cli={cod_cli}",
        )
        resp.raise_for_status()
        return resp.json()

    # --- Clients (Demandantes) ---

    async def get_client(self, cod_cli: str) -> dict:
        """Get client by unique code."""
        resp = await self._client.get(f"/clientes/?cod_cli={cod_cli}")
        resp.raise_for_status()
        return resp.json()

    async def search_client(
        self, telefono: str = "", email: str = "",
    ) -> list[dict]:
        """Search clients by phone and/or email."""
        params = {}
        if telefono:
            params["telefono"] = telefono
        if email:
            params["email"] = email
        resp = await self._client.get("/clientes/buscar/", params=params)
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else [data]

    # --- Enums ---

    async def get_property_types(self) -> list[dict]:
        """Get property type enum values."""
        resp = await self._client.get("/enums/?tipos=key_tipo")
        resp.raise_for_status()
        return resp.json()
