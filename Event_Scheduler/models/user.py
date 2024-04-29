from Event_Scheduler.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey



class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    pic_url: Mapped[str] = mapped_column(nullable=True)
    reviews = relationship("ReviewModel", lazy='dynamic', cascade="all, delete")
    ratings = relationship("RatingsModel", lazy='dynamic', cascade='all, delete')
    events = relationship("EventModel", back_populates='registered', secondary="user_events", lazy='dynamic')