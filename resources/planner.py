from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from models.planner import PlannerModel
from schemas import PlannerSchema
from db import db
from flask import request
from flask_smorest import Blueprint, abort
import re

planner_blp = Blueprint("Planners", "planners", description="Operations on planners")


@planner_blp.route("/planner_registration")
class PlannerRegister(MethodView):
    @planner_blp.arguments(PlannerSchema)
    def post(self, user_info):
        pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
        valid = re.match(pattern, user_info["email"])
        if not valid:
            abort(400, message="Invalid email")
        if db.session.execute(db.select(PlannerModel).where(PlannerModel.username==user_info["username"])).scalar():
            abort(409, message="username already exists")
        if db.session.execute(db.select(PlannerModel).where(PlannerModel.email==user_info["email"])).scalar():
            abort(409, message="email already exists")

        user = PlannerModel(
            username = user_info["username"],
            email = user_info["email"],
            password = user_info["password"],
            name = user_info["name"]
            )
        db.session.add(user)
        db.session.commit()
        
        result = db.session.execute(db.select(PlannerModel).where(PlannerModel.username==user_info["username"])).scalar_one()
        return {"message": "registerd", "username": result.username}, 201
