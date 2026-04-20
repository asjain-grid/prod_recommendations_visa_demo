from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.recommendations import router as recommendation_router
from app.core.database import init_databases


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_databases()
    yield


app = FastAPI(
    title="Visa Product Recommendation API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(recommendation_router)
