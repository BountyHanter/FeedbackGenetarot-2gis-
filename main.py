from fastapi import FastAPI

from config import init_db

from routers.user_routers import router as user_router
from routers.reviews_routers import router as reviews_router
from celery_service.celery_routers import router as celery_router

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["User"])
app.include_router(reviews_router, prefix="/api", tags=["Reviews"])
app.include_router(celery_router, prefix="/api", tags=["Celery"])


@app.on_event("startup")
async def startup_event():
    await init_db()
