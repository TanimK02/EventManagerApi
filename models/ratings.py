from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON, Boolean
from typing import Optional


class RatingsModel(db.Model):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(nullable=False)
    event: Mapped[int] = mapped_column(ForeignKey("events.id"))
    review_id: Mapped[Optional[int]] = mapped_column(ForeignKey("reviews.id"), nullable=True)
    review = relationship("ReviewModel", back_populates='rating', cascade="all, delete")
