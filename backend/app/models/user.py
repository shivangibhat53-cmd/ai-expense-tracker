from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.logging import logger


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True, autoincrement= True)
    email = Column(String, primary_key= True, index = True)
    hashed_password = Column(String, nullable = False)
    is_active = Column(Boolean, default = True)
    is_superuser = Column(Boolean, default = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    logger.info("Tables created")