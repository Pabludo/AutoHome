"""Prospect / owner models — mapped to Inmovilla API fields."""

from pydantic import BaseModel


class Owner(BaseModel):
    """Property owner from Inmovilla ``/propietarios/``."""

    cod_cli: int
    nombre: str = ""
    apellidos: str = ""
    email: str = ""
    telefono1: str = ""
    telefono2: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.nombre} {self.apellidos}".strip()

    @property
    def phone(self) -> str:
        return self.telefono1 or self.telefono2


class Prospect(BaseModel):
    """A prospect linking an Inmovilla property to its owner + Idealista URL."""

    cod_ofer: int
    ref: str
    owner: Owner
    idealista_url: str
    prospecto: bool = True
    clientify_contact_id: int | None = None
