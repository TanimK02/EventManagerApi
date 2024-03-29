from db import db

user_events = db.Table('user_events',
    db.Column('user', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event', db.Integer, db.ForeignKey('events.id'), primary_key=True)
)