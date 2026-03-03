from fastapi import FastAPI
from src.routers.project import router as project_router

app = FastAPI(title="Travel Planner API", version="1.0.0")
app.include_router(project_router, prefix="/api/v1")

@app.get("/")
async def health_chek():
    return {"status": "ok"}

