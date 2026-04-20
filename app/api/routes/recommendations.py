from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from app.core.config import RECOMMENDATION_API_KEY
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService


router = APIRouter(tags=["recommendations"])
service = RecommendationService()


@router.get("/customers/{customer_id}/recommendations", response_model=RecommendationResponse)
def get_customer_recommendations(
    customer_id: str,
    x_api_key: Optional[str] = Header(default=None),
) -> RecommendationResponse:
    if RECOMMENDATION_API_KEY and x_api_key != RECOMMENDATION_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    recommendations = service.get_recommendations(customer_id)
    if recommendations is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return recommendations
