from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import  AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from typing import Annotated
from fastapi.responses import JSONResponse
from ..models.user import User
from ..schemas import auth as user
from ..schemas.event import EventEnvelope
from ..services import jwt_handler as jwthandler
from ..database.session import get_db
from ..services.auth_service import for_Auth
from ..repository.user import update_verify_email
from ..services.email_verification import create_email_verification_token,verify_email_token
from ..messaging.nats_client import publish_event
auth = APIRouter()

@auth.post("/login")
async def login(request: Request, 
                cred: user.UserLogin, 
                response: Response,
                  auth_repo: for_Auth = Depends()):
    data = await auth_repo.login_user(cred)
    await publish_event(
            request.app.state.nats,
            subject="user.logged_in",
            event=EventEnvelope(
                event_type="user.logged_in",
                payload={
                    "username":data["username"],
                    "email":data["email"],
                    "access_token":data["access_token"]
                }
            )
        )
    return {"access_token":data["access_token"]}

@auth.post("/register")
async def register(request: Request,
                    cred: user.UserCreate, 
                    response: Response, 
                    auth_repo: for_Auth = Depends()):
    data = await auth_repo.create_user(cred)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="Registration failed. Please check your details and try again.")
    token=create_email_verification_token(data={"user_id":str(data["user_id"])})
    await publish_event(
        request.app.state.nats,
        subject="user.registered",
        event=EventEnvelope(
            event_type="user.registered",
            payload={
                "token":token,
                "url":f"http://localhost:8001/verify-email?token={token}",
                "email":data["email"],
                "message":"register successfull , Email verify"
            }
        )
    )
    return {"message": "Registration successful. Please Verify You Email"}

@auth.get("/me")
async def getuser(request: Request,
            response: Response, 
            current_user:dict=Depends(jwthandler.get_current_user)):
    await publish_event(
        request.app.state.nats,
        subject="user.get_user",
        event=EventEnvelope(
        event_type="user.get_user",
        payload={
                    "username":current_user["username"],
                    "email":current_user['email'],
                }
            ))
    
    return {
        "authenticated": True,
        "user":current_user
    }

@auth.get("/verify-email")
async def verify_email(request: Request,
                       response:Response,
    token: str = Query(..., description="The cryptographic token sent via email"),
    db: AsyncSession = Depends(get_db)
):
    user_id=await verify_email_token(token)
    if not user_id:
        raise HTTPException(status_code=401,detail="The verification link is invalid or has expired. Please request a new one.")
    
    result = await update_verify_email(db,user_id) 
    if not result:
        raise HTTPException(status_code=500,detail="Failed to verify email address. Account may already be verified or user does not exist.")
    
    return {"message": "Successfully verified email address."}



