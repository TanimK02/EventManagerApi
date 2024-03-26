from db import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey



class PlannerModel(db.Model):
    __tablename__ = "planners"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    pic_url: Mapped[str] = mapped_column(nullable=True)
    events = relationship("EventModel", lazy='dynamic', cascade="all, delete")
