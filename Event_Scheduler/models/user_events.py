from Event_Scheduler.db import Base
from sqlalchemy import Table, Column, Integer, ForeignKey

user_events = Table('user_events', Base.metadata,
    Column('user', Integer, ForeignKey('users.id'), primary_key=True),
    Column('event', Integer, ForeignKey('events.id'), primary_key=True)
)