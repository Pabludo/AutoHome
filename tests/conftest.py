"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_metrics():
    """Sample property metrics matching real Idealista stats card."""
    return {
        "property_id": "28751504",
        "url": "https://www.idealista.com/inmueble/111051259/",
        "timestamp": "2026-04-19T14:00:00Z",
        "metrics": {
            "visits": 303,
            "email_contacts": 15,
            "favorites": 32,
            "phone_contacts": None,
        },
        "last_updated": "Anuncio actualizado el 9 de abril",
    }


@pytest.fixture
def sample_owner():
    """Sample owner data matching real Inmovilla propietarios response."""
    return {
        "cod_cli": 37343138,
        "nombre": "MANUEL",
        "apellidos": "RAMIREZ",
        "email": "test@example.com",
        "telefono1": "",
        "telefono2": "661949813",
    }


@pytest.fixture
def sample_prospect(sample_owner):
    """Sample prospect matching real Inmovilla data."""
    return {
        "cod_ofer": 28751504,
        "ref": "PR12708",
        "owner": sample_owner,
        "idealista_url": "https://www.idealista.com/inmueble/111051259/",
        "prospecto": True,
    }
