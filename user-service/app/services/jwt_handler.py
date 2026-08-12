# JWT 
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

async def verify_token(token: str ,credentials_exception) -> TokenData:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        verified:bool | None =payload.get("verified")
        iat: int | None = payload.get("iat")

        if user_id is None:
            raise credentials_exception
        # if not verified:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Please verify Email. Check Your Mail"
        #     )

        return TokenData(user_id=user_id,
                         time=iat)

    except JWTError:
        raise credentials_exception


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(api_key_header_scheme)], 
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid X-USER-ID authentication header",
    )
    
    if not token:
        raise credentials_exception
    token_data =await verify_token(token, credentials_exception)
    
    try:
        user_uuid = uuid.UUID(token_data.user_id)
    except ValueError:
        raise credentials_exception

    user =await get_user(db=db,user_id=user_uuid)
    if user is None:
        raise credentials_exception  

    return user