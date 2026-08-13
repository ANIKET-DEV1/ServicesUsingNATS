import uuid

from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, status, Response
from ..models.user import User
from datetime import datetime, timedelta, timezone
from ..schemas.token import TokenData
from ..config import get_config
from ..database.session import get_db
from ..repository.user import get_user
from typing import Annotated
from sqlalchemy.ext.asyncio import  AsyncSession

api_key_header_scheme = APIKeyHeader(name="X-USER-ID", auto_error=False)
system = get_config()
SECRET_KEY = system.secret_key.get_secret_value()
ALGORITHM = system.algorithms.get_secret_value()


def create_email_verification_token(data: dict, expires_delta: timedelta = timedelta(hours=7)) -> str:
    now = datetime.now(timezone.utc)
    encoded_jwt = jwt.encode(
        {
            **data,
            "scope":"email-verification",
            "exp": datetime.now(timezone.utc) + expires_delta
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

async def verify_email_token(token: str ) -> TokenData:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("user_id")
        scope: str | None =payload.get("scope")
        if scope!="email-verification":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
               detail="Invalid Token the token is not for Email-verification")
        
        if user_id is None:
            raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN,
               detail="Invalid Token , user didnt found")

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            HTTPException(status_code=status.HTTP_403_FORBIDDEN,
               detail="Invalid Token")
  
        return user_uuid

    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                       detail="Invalid Token")