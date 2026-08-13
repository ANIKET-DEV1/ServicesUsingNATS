from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config import get_config
from .routes.users import router as users_router

settings = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        app.state.http_client = client
        yield



app = FastAPI(
    title="Task",
    lifespan=lifespan,
)

app.include_router(users_router, prefix="/users")


@app.get("/health", tags=["Health"])
async def health():
    user_service_status = "unreachable"
    try:
        resp = await app.state.http_client.get(
            f"{settings.USER_SERVICE_URL}/health", timeout=3.0
        )
        if resp.status_code == 200:
            user_service_status = "healthy"
        else:
            user_service_status = f"unhealthy (HTTP {resp.status_code})"
    except Exception:
        pass

    return JSONResponse(
        content={
            "gateway": "healthy",
            "user_service": user_service_status,
            "user_service_url": settings.USER_SERVICE_URL,
        }
    )
