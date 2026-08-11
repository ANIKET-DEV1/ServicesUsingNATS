from typing import Optional
import uuid
import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Text, String, Integer, ForeignKey, Boolean, UUID,Enum

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
        )
    username: Mapped[str] = mapped_column(
        String(20), 
        unique=True, 
        nullable=False
        )
    email: Mapped[str] = mapped_column(
        Text, 
        unique=True, 
        nullable=False
        )
    password: Mapped[str] = mapped_column(
        Text, 
        nullable=False
        )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False, 
        server_default="false", 
        nullable=False
        )