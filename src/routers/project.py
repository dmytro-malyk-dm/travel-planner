from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.crud.project import get_projects, get_project_or_404, create_project, update_project, delete_project
from src.schemas.project import TravelProjectInfo, TravelProjectCreate, TravelProjectUpdate


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[TravelProjectInfo])
async def list_projects(
        skip: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_async_session)
):
     return await get_projects(db, skip, limit)


@router.get("/{project_id}", response_model=TravelProjectInfo)
async def get_existing_project(
        project_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    return await get_project_or_404(db, project_id)


@router.post("/", response_model=TravelProjectInfo, status_code=status.HTTP_201_CREATED)
async def create_new_project(
        data: TravelProjectCreate,
        db: AsyncSession = Depends(get_async_session)
):
    return await create_project(db, data)


@router.patch("/{project_id}", response_model=TravelProjectInfo)
async def update_existing_project(
        project_id: int,
        data: TravelProjectUpdate,
        db: AsyncSession = Depends(get_async_session)
):
    project = await get_project_or_404(db, project_id)
    return await update_project(db, project, data)

@router.delete("/project_id", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_project(
        project_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    project = await get_project_or_404(db, project_id)
    return await delete_project(db, project)
