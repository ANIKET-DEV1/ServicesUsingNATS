from pydantic import BaseModel


class Notification(BaseModel):
    id: int
    user_id: int
    message: str
