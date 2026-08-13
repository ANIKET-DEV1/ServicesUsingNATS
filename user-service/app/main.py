from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database.connection import Base, engine
from .routes.users import auth
from .messaging.nats_client import connect_to_nats


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    nc = await connect_to_nats()
    app.state.nats = nc

    yield

    await nc.close()


app = FastAPI(
    title="User Service",
    lifespan=lifespan,
)

app.include_router(
    auth,
    prefix="/users",
    tags=["Users"],
)


@app.get("/health", tags=["Health"])
def health():
    return {
        "service": "user-service",
        "status": "healthy",
    }


