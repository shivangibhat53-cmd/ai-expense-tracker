from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func



class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key= True, index= True, autoincrement= True)

    message = Column(String, nullable = False)

    is_read = Column(Boolean, default = False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable = False)

    created_at = Column(DateTime(timezone=True),server_default= func.now())

    users = relationship("User", back_populates= "notifications")

