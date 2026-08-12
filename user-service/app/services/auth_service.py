from ..repository.base import BaseRepository
from fastapi import HTTPException,status,Response
from ..schemas import auth as user
from . import jwt_handler as jwthandler
from ..repository import user as crud_auth 
from ..models.user import User
from ..config import get_config

class for_Auth(BaseRepository):
    async def login_user(self, credential: user.UserLogin):
        user= await crud_auth.login(self.db,user_data=credential)
        if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid username or password.")
        token_payload = {
            "sub": str(user.id),
            "verified":user.is_verified,
        }
        access_token= jwthandler.create_access_token(data=token_payload)
        return {
            "access_token": access_token,
            "token_type": "bearer"
            }
    
    async def create_user(self,cred: user.UserCreate):
        data = await crud_auth.register_user(self.db,user_data=cred)
        
        return {"message":"register Successfull"}



        