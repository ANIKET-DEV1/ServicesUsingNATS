from pydantic import BaseModel


class UserCreated(BaseModel):
    id: int
    email: str
    name: str
