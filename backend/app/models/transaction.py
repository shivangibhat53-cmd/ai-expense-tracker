from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key = True, index = True, autoincrement= True)

    amount = Column(Float, nullable=False)

    type = Column(String, nullable=False)  # "income" or "expense"

    description = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="transactions")

    categories = relationship("Category", back_populates="transactions")