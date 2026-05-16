from fastapi import APIRouter
from app.api.v1.routes import auth
from app.core.logging import logger

logger.info("*************INISE V1/router.py***************")
api_router = APIRouter()
logger.info("Create api router")
api_router.include_router(auth.router)
logger.info("Include auth.router")