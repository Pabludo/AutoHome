"""Prospect and contact models."""

from pydantic import BaseModel


class Contact(BaseModel):
    """Client contact information."""

    name: str
    email: str | None = None
    phone: str | None = None


class Prospect(BaseModel):
    """A prospect from Inmovilla linking a client to a property."""

    prospect_id: str
    client: Contact
    property_id: str
    idealista_url: str
    inmovilla_status: str = "prospecto"
    clientify_contact_id: int | None = None
