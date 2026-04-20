from __future__ import annotations

from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import RecommendationItem, RecommendationResponse


class RecommendationService:
    def __init__(self, repository: RecommendationRepository | None = None) -> None:
        self.repository = repository or RecommendationRepository()

    def get_recommendations(self, customer_id: str) -> RecommendationResponse | None:
        customer = self.repository.get_customer(customer_id)
        if not customer:
            return None

        usage = self.repository.get_customer_usage(customer_id)
        challenges = self.repository.get_customer_challenges(customer_id)
        products = self.repository.get_products()
        features_by_product = self.repository.get_product_features()
        mappings_by_product = self.repository.get_product_challenge_mapping()

        owned_product_ids = {entry["product_id"] for entry in usage}
        usage_by_product = {entry["product_id"]: entry for entry in usage}
        challenge_priority = {
            entry["challenge_code"]: float(entry["priority_score"]) for entry in challenges
        }

        scored_items: list[dict[str, object]] = []
        for product in products:
            recommendation_type = self._get_recommendation_type(
                product=product,
                customer_type=customer["customer_type"],
                owned_product_ids=owned_product_ids,
            )
            if recommendation_type is None:
                continue

            score, reasons = self._score_product(
                product=product,
                recommendation_type=recommendation_type,
                customer=customer,
                challenge_priority=challenge_priority,
                mappings=mappings_by_product.get(product["product_id"], []),
                owned_product_ids=owned_product_ids,
                usage_by_product=usage_by_product,
            )
            if score <= 0:
                continue

            scored_items.append(
                {
                    "product": product,
                    "recommendation_type": recommendation_type,
                    "score": round(min(score, 1.0), 2),
                    "reasons": reasons,
                    "features": features_by_product.get(product["product_id"], []),
                }
            )

        scored_items.sort(key=lambda item: item["score"], reverse=True)
        recommendations = [
            RecommendationItem(
                product_id=item["product"]["product_id"],
                product_name=item["product"]["name"],
                recommendation_type=item["recommendation_type"],
                score=item["score"],
                rank=index,
                pricing=item["product"]["pricing"],
                regions=item["product"]["regions"].split(","),
                solution_features=item["features"],
                reasons=item["reasons"],
            )
            for index, item in enumerate(scored_items[:3], start=1)
        ]

        return RecommendationResponse(
            customer_id=customer["customer_id"],
            customer_name=customer["customer_name"],
            customer_type=customer["customer_type"],
            recommendations=recommendations,
        )

    def _get_recommendation_type(
        self,
        product: dict[str, object],
        customer_type: str,
        owned_product_ids: set[str],
    ) -> str | None:
        eligible_types = str(product["eligible_customer_types"]).split(",")
        if customer_type not in eligible_types:
            return None

        product_id = str(product["product_id"])
        if product_id in owned_product_ids:
            return None

        if product_id == "P002" and "P001" in owned_product_ids:
            return "upsell"

        if product_id != "P002":
            return "cross_sell"

        return None

    def _score_product(
        self,
        product: dict[str, object],
        recommendation_type: str,
        customer: dict[str, object],
        challenge_priority: dict[str, float],
        mappings: list[dict[str, object]],
        owned_product_ids: set[str],
        usage_by_product: dict[str, dict[str, object]],
    ) -> tuple[float, list[str]]:
        score = 0.15
        reasons: list[str] = ["Customer type is eligible for this product"]

        if customer["region"] in str(product["regions"]).split(","):
            score += 0.15
            reasons.append("Product is available in the customer region")

        for mapping in mappings:
            challenge_code = str(mapping["challenge_code"])
            if challenge_code not in challenge_priority:
                continue

            challenge_score = float(challenge_priority[challenge_code]) * float(mapping["relevance_score"])
            score += challenge_score * 0.5
            reasons.append(str(mapping["rationale"]))

        if recommendation_type == "upsell" and "P001" in owned_product_ids:
            aml_usage = usage_by_product["P001"]
            if float(aml_usage["usage_score"]) >= 0.65:
                score += 0.2
                reasons.append("Existing AML usage indicates readiness for a higher-tier solution")

            if float(customer["annual_volume"]) >= 1_500_000:
                score += 0.15
                reasons.append("Annual volume is high enough to justify premium capabilities")

        unique_reasons = []
        for reason in reasons:
            if reason not in unique_reasons:
                unique_reasons.append(reason)

        return score, unique_reasons[:4]
