import uuid
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..services.password_encryption import PasswordHasher
from fastapi import HTTPException, status
from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from ..models import user as models
from ..schemas import auth as user_schema


async def register_user(db: AsyncSession, user_data: user_schema.UserCreate)->models.User:
    try:
        duplicate_check =await db.execute(
            select(models.User).where(
                (models.User.email == user_data.email) | 
                (models.User.username == user_data.username)
            )
        )
        if duplicate_check.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email address is already registered."
            )
        hashed_password = PasswordHasher.hash(user_data.password.get_secret_value())
        db_user = models.User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password 
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return  {
            "user_id":db_user.id,
            "email":db_user.email
        }
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given credentials already exists."
        )
    except DataError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input data exceeds maximum allowed character limits."
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred during user registration."
        )
    
async def login(db:AsyncSession,user_data:user_schema.UserLogin):
    try:
        result=await db.execute(
            select(models.User).where(
                user_data.username==models.User.username
            ))
        user=result.scalar()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Username does not exist."
            )
        hashed_password=user.password
        passw = PasswordHasher.verify(user_data.password.get_secret_value(), hashed_password)
        if passw:
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during user authentication."
        )
    
async def get_user(db:AsyncSession,user_id:uuid.UUID):
    try :
        result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with the provided email address."
            )

        return {"username":user.username,
                "email":user.email,
                "is_verified":user.is_verified}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching user details."
        )
    



