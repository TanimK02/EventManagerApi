from typing import Literal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import JSON

my_literal = Literal[1, 2, 3, 4, 5]

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)