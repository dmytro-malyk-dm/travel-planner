from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.crud.places import (
    get_places,
    get_place_or_404,
    add_place_to_project,
    update_place,
)
from src.schemas.project import (
    ProjectPlaceBase,
    ProjectPlaceUpdate,
    ProjectPlaceResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["Places"],
)

@router.get("/", response_model=List[ProjectPlaceResponse])
async def list_places(
    project_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    return await get_places(db, project_id)


@router.get("/{place_id}", response_model=ProjectPlaceResponse)
async def get_place(
    project_id: int,
    place_id: int,
    db: AsyncSession = Depends(get_async_session),
):
    return await get_place_or_404(db, project_id, place_id)


@router.post("/", response_model=ProjectPlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int,
    data: ProjectPlaceBase,
    db: AsyncSession = Depends(get_async_session),
):
    return await add_place_to_project(db, project_id, data)


@router.patch("/{place_id}", response_model=ProjectPlaceResponse)
async def update_existing_place(
    project_id: int,
    place_id: int,
    data: ProjectPlaceUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    place = await get_place_or_404(db, project_id, place_id)
    return await update_place(db, place, data)
