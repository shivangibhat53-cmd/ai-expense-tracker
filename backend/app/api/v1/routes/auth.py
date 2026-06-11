from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse,ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token,create_refresh_token, create_email_verification_token
from app.services.auth_service import refresh_user_token,verify_email_token,generate_password_reset,reset_password
from app.db.deps import get_db
from app.models.user import User
from app.api.deps import get_current_user,get_current_active_superuser
from fastapi.security import OAuth2PasswordRequestForm
from app.services.email_service import send_verification_email


logger.info("**********INSIDE V1/Route/auth****************")
router = APIRouter(prefix = "/auth", tags = ["Auth"])
logger.info("Router created")
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)): 
    # Look for an existing user first
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("Router for registration")
    print(user.email)
    db_user = create_user(db, user.email, user.password)
    token = create_email_verification_token(db_user.email)
    logger.info("send_verification_email")
    send_verification_email(db_user.email,token)
    logger.info("After send_verification_email")
    return {"id": db_user.id, "email": db_user.email,
             "verification_token":token} # temporary (dev only)

@router.post("/login", response_model = Token)
def login( form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    logger.info("Router for login")
    if not db_user:
        raise HTTPException(status_code = 401, detail = "Invalid credentials") # Tells the client to use Bearer tokens
    
    if not db_user.is_verified:
        raise HTTPException(
        status_code=403,
        detail="Email not verified"
    )
    access_token = create_access_token({"sub": str(db_user.id), "type":"access"})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})
    logger.info("Creating token header.payload.signature")
    return {
        "access_token" :access_token,
        "refresh_token" : refresh_token,
        "token_type" : "bearer"
    }

@router.get("/verify-email")
def verify_email(
    token : str,
    db : Session = Depends(get_db)
):
    logger.info("Verifying email address")
    return verify_email_token(db, token)

@router.post("/refresh", response_model = Token)
def refresh_acccess_token(refresh_token : str):
    logger.info("Refreshing token")
    return  refresh_user_token(refresh_token)

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest , db : Session = Depends(get_db)):
    return generate_password_reset(db, request.email)

@router.post("/reset-password")
def reset_password_route(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password(db, request.token, request.new_password)


@router.get("/me", response_model = UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    logger.info("Got the current.user and email")

    return current_user

@router.get("/admin")
def admin_dashboard(
        current_user: User = Depends(get_current_active_superuser)):
    return {"message": "Welcome admin"}
