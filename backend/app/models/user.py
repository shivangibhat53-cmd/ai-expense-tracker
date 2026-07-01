from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.logging import logger
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True, autoincrement= True)

    email = Column(String, unique = True, index = True)

    hashed_password = Column(String, nullable = False)

    is_verified = Column(Boolean, default = False)

    is_active = Column(Boolean, default = True)

    is_superuser = Column(Boolean, default = False)

    created_at = Column(DateTime(timezone = True), server_default = func.now())

    categories = relationship("Category", back_populates = "user")

    transactions = relationship("Transaction", back_populates = "user")

    budgets = relationship("Budget", back_populates= "user")

    notifications = relationship("Notification", back_populates = "user")

    recurring_transactions = relationship("RecurringTransaction",back_populates="user",cascade="all, delete-orphan")
    
    logger.info("Tables created")
