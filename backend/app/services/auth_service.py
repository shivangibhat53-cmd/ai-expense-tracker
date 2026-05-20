from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.core.security import hash_password, verify_password,verify_access_token,create_access_token,create_refresh_token,create_password_reset_token
from app.core.logging import logger
logger.info("***********Inside auth service.py *********")
def create_user(db : Session, email :str, password : str):
    user = User(
        email = email,
        hashed_password = hash_password(password)
    )
    db.add(user)
    logger.info("USER ADDED")
    db.commit()
    logger.info("USER COMMITTED")
    db.refresh(user)
    logger.info("USER REFRESHED")

    return user

def authenticate_user(db:Session, email:str, password :str):
    user = db.query(User).filter(User.email == email).first()
    logger.info("AUTHENTICATING USER")
    if not user:
        # Generate a dummy verification step that mimics standard bcrypt computation time.
        # This keeps server response times identical whether an email exists or not. Timimg Attack Mitigation
        dummy_hash = "$2b$12$L7R6DksbH29Vj/5RsmP9be2M7g1wXq/O8p4B76L.bWwZEmwN0gTGW"
        verify_password(password, dummy_hash)
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def verify_email_token(db:Session, token:str):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid or expired token"
        )
    if payload.get("type") != "email_verification":
        raise HTTPException(
            status_code = 400,
            detail = "Invalid token type"
        )
    
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code = 404,
            detail = "User not found"
        )
    user.is_verified = True
    db.commit()

    return {
        "message": "Email verified successfully"
    }

def refresh_user_token(refresh_token: str):
    payload = verify_access_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code = 401,
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

def generate_password_reset(db:Session, email:str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        # SECURITY: don't reveal user existence
        return {"message": "If email exists, reset link sent"}
    
    token = create_password_reset_token(email)

    # send_email(email, token) → later
    logger.info(f"RESET TOKEN (DEV ONLY): {token}")

    return {"message" : "If email exists, reset link sent"}

def reset_password(db:Session, token :str, new_password : str):

    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code= 400,
            detail = "Invalid token"
        )

    if payload.get("type") != "password_reset":
        raise HTTPException(
            status_code = 400,
            detail = "Invalid token type"
        )
    
    email = payload.get("sub")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    
    user.hashed_password = hash_password(new_password)
    db.commit()

    return {"message" : "Password updated successfully"}


