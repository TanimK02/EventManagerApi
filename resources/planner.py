from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from models import PlannerModel
from schemas import PlannerSchema
from db import db
from flask import request, session
from flask_smorest import Blueprint, abort
import re
import bcrypt

planner_blp = Blueprint("Planners", "planners", description="Operations on planners")


@planner_blp.route("/planner_registration")
class PlannerRegister(MethodView):
    @planner_blp.arguments(PlannerSchema)
    def post(self, user_info):
        pattern_email= r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
        valid = re.match(pattern_email, user_info["email"])
        pass_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        valid2 = re.match(pass_pattern, user_info["password"])
        valid3 = re.match("^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", user_info["username"])
        if not valid:
            abort(400, message="Invalid email")
        if not valid2:
            abort(400, message="8 characters minimum. You also need at least one of each: one uppercase letter, one lowercase, one number, one special character'$!^%,etc'")
        if not valid3:
            abort(400, message="Username must be 8-20 characters long. No . or _")
        if db.session.execute(db.select(PlannerModel).where(PlannerModel.username==user_info["username"])).scalar():
            abort(409, message="username already exists")
        if db.session.execute(db.select(PlannerModel).where(PlannerModel.email==user_info["email"])).scalar():
            abort(409, message="email already exists")

        user = PlannerModel(
            username = user_info["username"],
            email = user_info["email"],
            password = bcrypt.hashpw(user_info["password"].encode('utf-8'), bcrypt.gensalt()),
            name = user_info["name"]
            )
        db.session.add(user)
        db.session.commit()
        
        result = db.session.execute(db.select(PlannerModel).where(PlannerModel.username==user_info["username"])).scalar_one()
        return {"message": "registerd", "username": result.username}, 201


@planner_blp.route("/planner_login")
class PlannerLogin(MethodView):

    def post(self):
        user_info = request.get_json()
        pattern_email= r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
        valid = re.match(pattern_email, user_info.get("email", ""))
        pass_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        valid2 = re.match(pass_pattern, user_info.get("password", ""))
        valid3 = re.match("^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", user_info.get("username", ""))
        if not (user_info.get("email", None) or user_info.get("username", None)):
            abort(400, message="Need email or username")
        if not user_info.get("password", None):
            abort(400, message="Need password.")
        if not (valid or valid2) and not valid3:
            abort(400, message="Invalid login credentials.")
        
        try:
            if user_info.get("username", None):
                user = db.session.execute(db.select(PlannerModel).where(PlannerModel.username==user_info["username"])).scalar_one()
            elif user_info.get("email", None):
                user = db.session.execute(db.select(PlannerModel).where(PlannerModel.email==user_info["email"])).scalar_one()
            else:
                abort(400, message="Need username or email")
        except SQLAlchemyError:
            abort(404, message="User does not exist")
        if bcrypt.checkpw(user_info["password"].encode('utf-8'), user.password):
            session["user_id"] = user.id
            return {"message": "logged in"}, 200
        else:
            abort(401)