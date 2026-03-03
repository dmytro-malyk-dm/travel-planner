from fastapi import FastAPI

app = FastAPI(title="Travel Planner API", version="1.0.0")


@app.get("/")
async def health_chek():
    return {"status": "ok"}

