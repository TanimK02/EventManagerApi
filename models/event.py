import datetime
from typing import Optional
from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, JSON, Boolean


class EventModel(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator: Mapped[str] = mapped_column(String(), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("planners.id"))
    editors = relationship("PlannerModel", back_populates='events', secondary="event_editors")
    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(), nullable=True)
    date: Mapped[Optional[datetime.date]]
    price: Mapped[Optional[float]] = mapped_column(nullable=True)
    max_attendants: Mapped[Optional[int]] = mapped_column(nullable=True)
    attendants: Mapped[Optional[int]] = mapped_column(default=0)
    created_at: Mapped[Optional[datetime.date]]
    updated_at: Mapped[Optional[datetime.date]]
    published_at: Mapped[Optional[datetime.date]]
    published = mapped_column(Boolean(), default=False)
    rating: Mapped[float] = mapped_column(nullable=False, default=0)
    ratings = relationship("RatingsModel", lazy="dynamic", cascade="all, delete")
    reviews = relationship("ReviewModel", lazy='dynamic', cascade="all, delete")
    registered = relationship("UserModel", back_populates='events', secondary="user_events", lazy='dynamic')
    status: Mapped[str] = mapped_column(String(), nullable=True)
