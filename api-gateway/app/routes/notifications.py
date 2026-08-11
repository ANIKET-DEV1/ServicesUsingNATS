from fastapi import APIRouter

router = APIRouter()


@router.post("/send")
async def send_notification():
    # Proxy to notification-service in a real setup
    return {"message": "Notification request received (proxy placeholder)"}
