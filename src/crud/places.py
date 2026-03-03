from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.project import ProjectPlace, TravelProject
from src.schemas.project import ProjectPlaceBase, ProjectPlaceUpdate
from src.services.art_institute import art_institute_client

MAX_PLACES_PER_PROJECT = 10


async def get_place_or_404(
        db: AsyncSession,
        project_id: int,
        place_id: int
) -> ProjectPlace:
    result = await db.execute(
        select(ProjectPlace)
        .where(
            ProjectPlace.id == place_id,
            ProjectPlace.project_id == project_id
        )
    )
    place = result.scalar_one_or_none()

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place {place_id} not fount in project {project_id}"
        )
    return place


async def get_places(
        db: AsyncSession,
        project_id: int
) -> List[ProjectPlace]:
    result = await db.execute(
        select(ProjectPlace)
        .where(ProjectPlace.project_id == project_id)
        .order_by(ProjectPlace.created_at.asc())
    )
    return result.scalars().all()


async def _check_project_completion(
    db: AsyncSession,
    project: TravelProject,
) -> None:
    """
    Перевіряє чи всі місця в проекті відвідані.
    Якщо так — позначає проект як completed.
    """
    if not project.places:
        return

    all_visited = all(place.is_visited for place in project.places)
    if all_visited and not project.is_completed:
        project.is_completed = True
        await db.commit()


async def add_place_to_project(
        db: AsyncSession,
        project_id: int,
        data: ProjectPlaceBase,
) -> ProjectPlace:
    result = await db.execute(
        select(TravelProject)
        .where(TravelProject.id == project_id)
        .options(selectinload(TravelProject.places))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    if len(project.places) >= MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project cannot have more than {MAX_PLACES_PER_PROJECT} places",
        )

    existing = await db.execute(
        select(ProjectPlace).where(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == data.external_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This place is already in the project",
        )
    artwork = await art_institute_client.get_artwork(data.external_id)
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork {data.external_id} not found in Art Institute API",
        )

    place = ProjectPlace(
        project_id=project_id,
        external_id=data.external_id,
        notes=data.notes
    )
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return place


async def update_place(
        db: AsyncSession,
        place: ProjectPlace,
        data: ProjectPlaceUpdate
) -> ProjectPlace:
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(place, field, value)

    await db.commit()
    await db.refresh(place)

    result = await db.execute(
        select(TravelProject)
        .where(TravelProject.id == place.project_id)
        .options(selectinload(TravelProject.places))
    )

    project = result.scalar_one_or_none()
    await _check_project_completion(db, project)
    return place