import datetime
from typing import Optional
from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class EventModel(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(), nullable=True)
    price: Mapped[Optional[int]] = mapped_column(nullable=True)
    creator: Mapped[str] = mapped_column(String(), nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("planners.id"))
    editors_id: Mapped[str] = mapped_column(String(), nullable=True)
    created_at: Mapped[Optional[datetime.date]]
    updated_at: Mapped[Optional[datetime.date]]
    published_at: Mapped[Optional[datetime.date]]
    status: Mapped[str] = mapped_column(nullable=True)
