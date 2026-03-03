from typing import List

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.util import await_only, has_compiled_ext

from src.crud.places import MAX_PLACES_PER_PROJECT
from src.models.project import TravelProject, ProjectPlace
from src.schemas.project import TravelProjectCreate, TravelProjectUpdate
from src.services.art_institute import art_institute_client


async def get_project_or_404(db: AsyncSession, project_id: int) -> TravelProject:
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
    return project


async def get_projects(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
) -> List[TravelProject]:
    result = await db.execute(
        select(TravelProject)
        .options(selectinload(TravelProject.places))
        .offset(skip)
        .limit(limit)
        .order_by(TravelProject.created_at.desc())
    )
    return result.scalars().all()


async def create_project(
    db: AsyncSession,
    data: TravelProjectCreate,
) -> TravelProject:
    place_ids = data.place_ids or []

    if len(place_ids) > MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add more than {MAX_PLACES_PER_PROJECT} places",
        )

    if len(place_ids) != len(set(place_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate place IDs in request",
        )

    for external_id in place_ids:
        artwork = await art_institute_client.get_artwork(external_id)
        if not artwork:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork {external_id} not found in Art Institute API",
            )

    project = TravelProject(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    db.add(project)
    await db.flush()

    for external_id in place_ids:
        place = ProjectPlace(project_id=project.id, external_id=external_id)
        db.add(place)

    await db.commit()
    return await get_project_or_404(db, project.id)


async def update_project(
        db: AsyncSession,
        project: TravelProject,
        data: TravelProjectUpdate,
) -> TravelProject:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(
        db: AsyncSession,
        project: TravelProject
) -> None:
    has_visited = any(place.is_visited for place in project.places)
    if has_visited:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot daletete project with visited places"
        )
    await db.delete(project)
    await db.commit()
