import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True
    }


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    message: str = Field(
        ...,
        min_length=1,
        max_length=500
    )


class NotificationResponse(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    message: str
    status: str
    created_at: datetime