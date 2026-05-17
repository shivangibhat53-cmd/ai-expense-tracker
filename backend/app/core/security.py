from passlib.context import CryptContext
from .logging import logger
from datetime import datetime,timedelta, timezone
from app.core.config import settings
from jose import jwt, JWTError

from app.core.config import settings


logger.info("*********Inside Security.py***********")
pwd_context = CryptContext(schemes = ["argon2"], deprecated = "auto")

def hash_password(password: str) -> str:
    logger.info("Creating the hashed password")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.info("Verifying the hashed password")
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict, expires_delta:timedelta | None = None) -> str:
    logger.info("CREATING ACCESS TOKENS")
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm = settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days = settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update(
        {"exp":expire,
         "type" : "refresh"}
    )

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm = settings.ALGORITHM
    )

def verify_access_token(token : str):
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY,
                             algorithms = [settings.ALGORITHM])
        return payload
    except JWTError:
        return None