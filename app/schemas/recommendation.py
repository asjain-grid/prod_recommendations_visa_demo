from __future__ import annotations

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    product_id: str
    product_name: str
    recommendation_type: str
    score: float
    rank: int
    pricing: float
    regions: list[str]
    solution_features: list[str]
    reasons: list[str]


class RecommendationResponse(BaseModel):
    customer_id: str
    customer_name: str
    customer_type: str
    recommendations: list[RecommendationItem]
