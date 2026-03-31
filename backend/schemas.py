from typing import Optional

from pydantic import BaseModel, Field


class ForecastCreate(BaseModel):
    base_date: str = Field(..., examples=["20260331"])
    base_time: str = Field(..., examples=["0500"])
    fcst_date: str = Field(..., examples=["20260331"])
    fcst_time: str = Field(..., examples=["0900"])
    category: str = Field(..., examples=["TMP"])
    fcst_value: str = Field(..., examples=["14"])
    nx: int = Field(..., examples=[60])
    ny: int = Field(..., examples=[127])
    location_name: str = Field(default="서울", examples=["서울"])


class ForecastUpdate(BaseModel):
    fcst_value: Optional[str] = None
    location_name: Optional[str] = None


class FetchRequest(BaseModel):
    base_date: str = Field(..., examples=["20260331"])
    base_time: str = Field(..., examples=["0500"])
    nx: int = Field(..., examples=[60])
    ny: int = Field(..., examples=[127])
    location_name: str = Field(default="서울", examples=["서울"])
