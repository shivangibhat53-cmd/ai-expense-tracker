from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.oauth2 import oauth2_scheme
from app.core.security import verify_access_token
from app.db.deps import get_db
from app.models.user import User
from app.core.config import settings
from app.core.logging import logger

def get_current_user(
        token : str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    logger.info("Verifying JWT token:")

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token",headers={"WWW-Authenticate": "Bearer"}
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid access token"
        )
                 
    user_id  = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    logger.info(f"Authenticated user:{user.email}")

    return user

def get_current_active_superuser(
        current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code = 403,
            detail = "Not enough permissions"
        )
    return current_user

