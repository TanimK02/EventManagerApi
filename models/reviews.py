import datetime
from typing import Optional
from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class ReviewModel(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    rating = relationship("RatingsModel", back_populates="review", lazy='dynamic', cascade="all, delete")
    rate = Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[Optional[datetime.date]]
    updated_at: Mapped[Optional[datetime.date]]