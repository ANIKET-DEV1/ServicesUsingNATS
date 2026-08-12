from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database.connection import Base, engine
from .routes.users import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="User Service",
    lifespan=lifespan
)

app.include_router(
    auth,
    prefix="/users",
    tags=["Users"]
)


@app.get("/health")
def health():
    return {
        "service": "user-service",
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('user-service.app.main', host="127.0.0.1", port=8001, reload=True)
