from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.database import init_databases
from app.main import app


def test_recommendations_for_existing_customer() -> None:
    init_databases()
    with TestClient(app) as client:
        response = client.get("/customers/C001/recommendations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["customer_id"] == "C001"
    assert payload["recommendations"]
    assert payload["recommendations"][0]["product_id"] == "P004"


def test_returns_404_for_missing_customer() -> None:
    init_databases()
    with TestClient(app) as client:
        response = client.get("/customers/UNKNOWN/recommendations")

    assert response.status_code == 404
