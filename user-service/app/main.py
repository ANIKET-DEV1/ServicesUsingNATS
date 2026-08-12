from fastapi import FastAPI

from .database.connection import Base, engine
from .routes.users import auth
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service"
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
    uvicorn.run(app, host="127.0.0.1", port=8001)