from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from app.db.base import Base

from sqlalchemy.orm import relationship



class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key= True, index = True, autoincrement= True)

    amount = Column(Float, nullable = False)

    month = Column(Integer, nullable = False)

    year = Column(Integer, nullable = False)

    warning_sent = Column(Boolean, default = False)

    exceeded_sent = Column(Boolean, default = False)

    user_id = Column(Integer, ForeignKey("users.id"))

    category_id = Column(Integer, ForeignKey("categories.id"))

    user = relationship("User", back_populates = "budgets")

    category = relationship("Category", back_populates = "budgets")
