from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users():
    # This gateway would normally proxy to user-service
    return {"message": "List users (proxy placeholder)"}
