from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database.connection import Base, engine
from .routes.users import auth
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .messaging.nats_client import connect_to_nats

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@asynccontextmanager
async def lifespan(app: FastAPI):

    nc = await connect_to_nats()

    app.state.nats = nc

    yield

    await nc.close()


app = FastAPI(lifespan=lifespan)


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
