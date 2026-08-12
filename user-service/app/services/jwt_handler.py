# JWT 
import uuid

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, status, Response
from ..models.user import User
from datetime import datetime, timedelta, timezone
from ..schemas.token import TokenData
from ..config import get_config
from ..database.session import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import  AsyncSession

system = get_config()
SECRET_KEY = system.secret_key.get_secret_value()
ALGORITHM = system.algorithms


def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
    now = datetime.now(timezone.utc)
    encoded_jwt = jwt.encode(
        {
            **data,
            'iat': int(now.timestamp()),
            "exp": datetime.now(timezone.utc) + expires_delta
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

async def verify_token(token: str) -> TokenData:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        verified:bool | None =payload.get("verified")
        iat: int | None = payload.get("iat")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired session"
            )
        if not verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify Email. Check Your Mail"
            )

        return TokenData(user_id=user_id,
                         time=iat)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired session"
        )




