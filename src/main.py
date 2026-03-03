from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.routers.project import router as project_router
from src.services.art_institute import art_institute_client


@asynccontextmanager
async def lifespan(app: FastAPI):

    await art_institute_client.start()
    yield

    await art_institute_client.stop()

app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(project_router, prefix="/api/v1")

@app.get("/")
async def health_chek():
    return {"status": "ok"}

