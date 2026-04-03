from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100)


class ReviewGenerationRequest(BaseModel):
    menu_name: str = Field(..., min_length=1, max_length=100)
    keyword: str = Field(..., min_length=1, max_length=50)
