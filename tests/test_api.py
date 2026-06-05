"""
Testy jednostkowe — interfejs API FastAPI.

Testuje poprawność działania punktów końcowych (endpoints)
oraz walidację danych wejściowych.
"""

import os
import sys
from fastapi.testclient import TestClient

# Dodaj katalog główny projektu do ścieżki importów
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import app

client = TestClient(app)


def test_health_check():
    """Sprawdza czy endpoint health-check działa poprawnie."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data


def test_predict_endpoint_valid_data():
    """Sprawdza czy predykcja zwraca prawidłową strukturę odpowiedzi dla poprawnych danych."""
    payload = {
        "gr_liv_area": 1500,
        "total_bsmt_sf": 800,
        "first_flr_sf": 1000,
        "second_flr_sf": 0,
        "lot_area": 8000,
        "garage_cars": 2,
        "garage_area": 400,
        "overall_qual": 7,
        "year_built": 1995,
        "year_remod": 2005,
        "full_bath": 2,
        "half_bath": 0,
        "bedrooms": 3,
        "total_rooms": 7,
        "fireplaces": 1,
        "kitchen_qual": "TA",
        "exter_qual": "TA",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price_usd" in data
    assert "predicted_price_pln" in data
    assert "price_range_low" in data
    assert "price_range_high" in data
    assert data["predicted_price_usd"] > 0
    assert data["price_range_low"] < data["predicted_price_usd"] < data["price_range_high"]


def test_predict_endpoint_invalid_data():
    """Sprawdza czy walidacja FastAPI odrzuca niepoprawne dane (np. za wysoka jakość)."""
    payload = {
        "gr_liv_area": 1500,
        "overall_qual": 11,  # Dozwolone 1-10
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
