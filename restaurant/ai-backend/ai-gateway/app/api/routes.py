from fastapi import APIRouter

from app.schemas.requests import RecommendationRequest, ReviewGenerationRequest
from app.services.recommendation_service import recommend_menu
from app.services.review_service import generate_review

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"service": "ai-gateway", "status": "ok"}


@router.post("/recommend-menu")
def recommend(request: RecommendationRequest) -> dict:
    return recommend_menu(request.keyword)


@router.post("/write-review")
def write_review(request: ReviewGenerationRequest) -> dict:
    return generate_review(request.menu_name, request.keyword)


@router.get("/busy-status")
def busy_status() -> dict:
    return {
        "status": "NORMAL",
        "estimatedWaitMinutes": 12
    }
