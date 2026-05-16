from pydantic import BaseModel, EmailStr
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
    token_type :str = "bearer"