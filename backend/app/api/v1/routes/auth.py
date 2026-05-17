from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token,create_refresh_token,verify_access_token
from app.db.deps import get_db
from app.models.user import User
from app.api.deps import get_current_user,get_current_active_superuser
from fastapi.security import OAuth2PasswordRequestForm


logger.info("**********INSIDE V1/Route/auth****************")
router = APIRouter(prefix = "/auth", tags = ["Auth"])
logger.info("Router created")
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user.email, user.password)
    # Look for an existing user first
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("Router for registration")
    return {"id": db_user.id, "email": db.user_email}

@router.post("/login", response_model = Token)
def login( form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    logger.info("Router for login")
    if not db_user:
        raise HTTPException(status_code = 401, detail = "Invalid credentials") # Tells the client to use Bearer tokens
    
    access_token = create_access_token({"sub": str(db_user.id), "type":"access"})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})
    logger.info("Creating token header.payload.signature")
    return {
        "access_token" :access_token,
        "refresh_token" : refresh_token,
        "token_type" : "bearer"
    }

@router.post("/refresh", response_model = Token)
def refresh_token(refresh_token : str):
    payload = verify_access_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_Code = 401,
            detail = "Invalid refresh token"
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token type"
        )
    
    user_id = payload.get("sub")

    access_token = create_access_token({"sub" : user_id, "type" : "access"})
    new_refresh_token = create_refresh_token({"sub": user_id})

    return {
        "access_token" : access_token,
        "refresh_token" : new_refresh_token,
        "token_type" : "bearer"    }



@router.get("/me", response_model = UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    logger.info("Got the current.user and email")

    return current_user

@router.get("/admin")
def admin_dashboard(
        current_user:User = Depends(get_current_active_superuser)):
    return {"message": "Welcome admin"}
