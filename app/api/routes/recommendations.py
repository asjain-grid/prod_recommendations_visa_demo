from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService


router = APIRouter(tags=["recommendations"])
service = RecommendationService()


@router.get("/customers/{customer_id}/recommendations", response_model=RecommendationResponse)
def get_customer_recommendations(customer_id: str) -> RecommendationResponse:
    recommendations = service.get_recommendations(customer_id)
    if recommendations is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return recommendations
