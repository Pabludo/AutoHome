"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_metrics():
    """Sample property metrics for testing."""
    return {
        "property_id": "111029821",
        "url": "https://www.idealista.com/inmueble/111029821/",
        "timestamp": "2026-04-19T14:00:00Z",
        "metrics": {
            "visits": 1619,
            "email_contacts": 11,
            "favorites": 88,
            "phone_contacts": None,
        },
        "last_updated": "Anuncio actualizado el 18 de diciembre",
    }


@pytest.fixture
def sample_prospect():
    """Sample prospect data for testing."""
    return {
        "prospect_id": "INM-12345",
        "client": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+34600000000",
        },
        "property_id": "111029821",
        "idealista_url": "https://www.idealista.com/inmueble/111029821/",
        "inmovilla_status": "prospecto",
    }
