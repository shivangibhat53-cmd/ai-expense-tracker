from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class RecurringTransaction(Base):

    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    merchant = Column(String, nullable=False)

    frequency = Column(String, nullable=False)

    average_amount = Column(Float, nullable=False)

    confidence = Column(Float, nullable=False)

    occurrences = Column(Integer, nullable=False)

    next_expected_date = Column(DateTime)

    status = Column(
        String,
        default="ACTIVE",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )

    user = relationship(
        "User",
        back_populates="recurring_transactions",
    )