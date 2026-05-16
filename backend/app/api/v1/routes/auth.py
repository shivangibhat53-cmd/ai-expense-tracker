from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token
from app.db.deps import get_db
from app.models.user import User

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
def login(user : UserLogin, db:Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    logger.info("Router for login")
    if not db_user:
        raise HTTPException(status_code = 401, detail = "Invalid credentials", headers={"WWW-Authenticate": "Bearer"}) # Tells the client to use Bearer tokens
    
    token = create_access_token({"sub": db_user.email})
    logger.info("Creating token header.payload.signature")
    return {
        "access_token" :token,
        "token_type" : "bearer"
    }