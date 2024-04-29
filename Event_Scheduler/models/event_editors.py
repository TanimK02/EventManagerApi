
from Event_Scheduler.db import Base
from sqlalchemy import Table, Column, Integer, ForeignKey

event_editors = Table('event_editors', Base.metadata,
    Column('editor', Integer, ForeignKey('planners.id'), primary_key=True),
    Column('event', Integer, ForeignKey('events.id'), primary_key=True)
)