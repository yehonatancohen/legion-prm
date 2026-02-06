from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import User

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    async with AsyncSessionLocal() as session:
        # We assume username is phone or unique identifier? User model says phone is unique.
        # But OAuth2 form has username field.
        result = await session.execute(select(User).where(User.phone == form_data.username))
        user = result.scalars().first()
        
        # NOTE: In real app, we need password field in User model. 
        # The current User model lacks a password_hash field!
        # I must add password_hash to User model.
        
        if not user or not security.verify_password(form_data.password, user.hashed_password):
             raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
