"""Property and metrics models."""

from datetime import datetime

from pydantic import BaseModel


class PropertyMetrics(BaseModel):
    """Metrics scraped from the Idealista 'Estadísticas' card."""

    visits: int | None = None
    email_contacts: int | None = None
    phone_contacts: int | None = None
    favorites: int | None = None


class PropertySnapshot(BaseModel):
    """A point-in-time snapshot of property metrics."""

    property_id: str
    url: str
    timestamp: datetime
    metrics: PropertyMetrics
    last_updated: str | None = None


class PortalPublication(BaseModel):
    """Idealista publication info from Inmovilla extrainfo."""

    state: str | None = None
    message: str | None = None
    alerts_number: str | None = None
    quality_percentage: str | None = None
    publication_url: str | None = None


class Property(BaseModel):
    """Property from Inmovilla with Idealista publication data.

    Maps to Inmovilla ``/propiedades/?cod_ofer=`` response.
    """

    cod_ofer: int
    ref: str
    nodisponible: bool = False
    prospecto: bool = False
    referenciacol: str | None = None
    idealista_url: str | None = None
    precio: float | None = None
    precioinmo: float | None = None
    m_cons: float | None = None
    habitaciones: int | None = None
    banyos: int | None = None
    latitud: str | None = None
    longitud: str | None = None
    keycli: str | None = None
    fechaact: str | None = None
