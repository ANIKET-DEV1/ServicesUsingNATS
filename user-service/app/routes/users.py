from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import  AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from typing import Annotated
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from ..models.user import User
from ..schemas import auth as user
from ..services import jwt_handler as jwthandler
from ..database.session import get_db
from ..services.auth_service import for_Auth
auth = APIRouter(prefix="/user", tags=["user-services"])

@auth.post("/login")
async def login(request: Request, 
                cred: user.UserLogin, 
                response: Response,
                  auth_repo: for_Auth = Depends()):
    data = await auth_repo.login_user(cred)
    
    return data

@auth.post("/register")
async def register(request: Request,
                    cred: user.UserCreate, 
                    response: Response, 
                    auth_repo: for_Auth = Depends()):
    maybe = await auth_repo.create_user(cred)
    if not maybe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="Registration failed. Please check your details and try again.")
    return {"message": "Registration successful."}

