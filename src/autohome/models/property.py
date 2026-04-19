"""Property and metrics models."""

from datetime import datetime

from pydantic import BaseModel


class PropertyMetrics(BaseModel):
    """Metrics scraped from a single Idealista property listing."""

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


class Property(BaseModel):
    """Property aggregate with metadata."""

    property_id: str
    idealista_url: str
    address: str | None = None
    price: float | None = None
    status: str = "active"
