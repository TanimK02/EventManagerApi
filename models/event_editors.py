
from db import db

event_editors = db.Table('event_editors',
    db.Column('editor', db.Integer, db.ForeignKey('planners.id'), primary_key=True),
    db.Column('event', db.Integer, db.ForeignKey('events.id'), primary_key=True)
)