from fastapi import FastAPI

from .database import Base, engine
from .routes.users import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service"
)

app.include_router(
    router,
    prefix="/users",
    tags=["Users"]
)


@app.get("/health")
def health():
    return {
        "service": "user-service",
        "status": "healthy"
    }