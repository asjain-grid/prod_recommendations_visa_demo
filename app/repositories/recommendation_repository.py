from __future__ import annotations

from typing import Any

from app.core.database import get_customer_connection, get_products_connection


class RecommendationRepository:
    def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        with get_customer_connection() as connection:
            row = connection.execute(
                """
                SELECT customer_id, customer_name, customer_type, segment, region, annual_volume
                FROM customers
                WHERE customer_id = ?
                """,
                (customer_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_customer_usage(self, customer_id: str) -> list[dict[str, Any]]:
        with get_customer_connection() as connection:
            rows = connection.execute(
                """
                SELECT customer_id, product_id, usage_level, usage_score, feedback_summary, feedback_sentiment
                FROM customer_product_usage
                WHERE customer_id = ?
                """,
                (customer_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_customer_challenges(self, customer_id: str) -> list[dict[str, Any]]:
        with get_customer_connection() as connection:
            rows = connection.execute(
                """
                SELECT challenge_code, challenge_description, priority_score
                FROM customer_business_challenges
                WHERE customer_id = ?
                ORDER BY priority_score DESC
                """,
                (customer_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_products(self) -> list[dict[str, Any]]:
        with get_products_connection() as connection:
            rows = connection.execute(
                """
                SELECT product_id, name, description, pricing, regions, category, eligible_customer_types
                FROM products
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_product_features(self) -> dict[str, list[str]]:
        with get_products_connection() as connection:
            rows = connection.execute(
                """
                SELECT product_id, feature_name
                FROM product_solution_features
                ORDER BY feature_id
                """
            ).fetchall()

        grouped: dict[str, list[str]] = {}
        for row in rows:
            grouped.setdefault(row["product_id"], []).append(row["feature_name"])
        return grouped

    def get_product_challenge_mapping(self) -> dict[str, list[dict[str, Any]]]:
        with get_products_connection() as connection:
            rows = connection.execute(
                """
                SELECT product_id, challenge_code, relevance_score, rationale
                FROM product_challenge_mapping
                """
            ).fetchall()

        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            grouped.setdefault(row["product_id"], []).append(dict(row))
        return grouped
