from sqlalchemy.orm import declarative_base
from app.core.logging import logger

logger.info("Inside the base.py")
Base = declarative_base()