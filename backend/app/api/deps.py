from typing import Generator, Optional
import uuid as uuid_lib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.future import select
from app.core import security
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

async def get_current_user(token: str = Depends(reusable_oauth2)) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data_sub = payload.get("sub")
        if token_data_sub is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        # Convert string to UUID
        try:
            user_id = uuid_lib.UUID(token_data_sub)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user ID format in token",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (any role)."""
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are an admin."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Alias for get_current_admin_user (backward compatibility)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user

