from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key = True, index = True, autoincrement= True)

    name = Column(String, nullable = False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)

    user = relationship("User", back_populates = "categories")

    transactions = relationship("Transaction", back_populates="category")

    budgets = relationship("Budget", back_populates = "category")

