from fastapi import FastAPI

from .messaging import consumers

app = FastAPI(title="notification-service")


@app.get("/")
async def root():
    return {"service": "notification-service", "status": "ok"}
