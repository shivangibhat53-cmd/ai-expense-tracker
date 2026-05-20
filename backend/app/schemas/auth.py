from pydantic import BaseModel, EmailStr, ConfigDict
from app.core.logging import logger

class UserCreate(BaseModel):
    logger.info("CREATED USERCREATE")
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    logger.info("CREATED USERLOGIN")
    email : EmailStr
    password :str

class Token(BaseModel):
    logger.info("CREATED TOKEN")
    access_token :str
    refresh_token : str
    token_type :str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes = True)

class ForgotPasswordRequest(BaseModel):
    email : EmailStr

class ResetPasswordRequest(BaseModel):
    token : str
    new_password : str