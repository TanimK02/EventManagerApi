import datetime
from typing import Optional
from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON

class EventModel(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator: Mapped[str] = mapped_column(String(), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("planners.id"))
    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_attendants: Mapped[Optional[int]] = mapped_column(nullable=True)
    attendants: Mapped[Optional[int]] = mapped_column(default=0)
    editors_id: Mapped[str] = mapped_column(String(), nullable=True)
    created_at: Mapped[Optional[datetime.date]]
    updated_at: Mapped[Optional[datetime.date]]
    published_at: Mapped[Optional[datetime.date]]
    rating = mapped_column(JSON(), default={
    "1_star": 0,
    "2_star": 0,
    "3_star": 0,
    "4_star": 0,
    "5_star": 0
    })
    reviews = relationship("ReviewModel", lazy='dynamic', cascade="all, delete")
    status: Mapped[str] = mapped_column(String(), nullable=True)
