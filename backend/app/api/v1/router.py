from fastapi import APIRouter
from app.api.v1.routes import auth,transactions,categories,budgets,notifications
from app.core.logging import logger

logger.info("*************INISE V1/router.py***************")
api_router = APIRouter()
logger.info("Create api router")
api_router.include_router(auth.router)
logger.info("Include auth.router")
api_router.include_router(transactions.router)
logger.info("Include transaction.router")
api_router.include_router(categories.router)
logger.info("Include budgets.router")
api_router.include_router(budgets.router)
logger.info("Include notifications.router")
api_router.include_router(notifications.router)