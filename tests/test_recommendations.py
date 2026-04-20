from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.database import get_customer_connection, get_products_connection, init_databases
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


def test_seed_data_contains_100_products_and_100_customers() -> None:
    init_databases()

    with get_products_connection() as product_connection:
        product_count = product_connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    with get_customer_connection() as customer_connection:
        customer_count = customer_connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

    assert product_count == 100
    assert customer_count == 100
