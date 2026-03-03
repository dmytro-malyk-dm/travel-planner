from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ProjectPlaceBase(BaseModel):
    external_id: int
    notes: Optional[str] = None


class ProjectPlaceResponse(ProjectPlaceBase):
    id: int
    is_visited: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TravelProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    place_ids: Optional[List[int]] = []


class TravelProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class TravelProjectInfo(BaseModel):
    id: int
    description: Optional[str] = None
    start_date: Optional[date] = None
    is_completed: bool
    created_at: datetime
    places: List[ProjectPlaceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectPlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None
