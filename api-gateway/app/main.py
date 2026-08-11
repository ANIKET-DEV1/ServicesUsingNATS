from fastapi import FastAPI
from .routes import users, notifications

app = FastAPI(title="API Gateway")

app.include_router(users.router, prefix="/users")
app.include_router(notifications.router, prefix="/notifications")

@app.get("/")
async def root():
    return {"service": "api-gateway", "status": "ok"}
