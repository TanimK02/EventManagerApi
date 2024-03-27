from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from models import PlannerModel, EventModel
from schemas import PlannerSchema, EventSchema
from db import db
from flask import request, jsonify, current_app, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
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
            ad_claims = {"Model": "Planner"}
            access_token = create_access_token(identity=user.id, additional_claims=ad_claims)
            return jsonify(access_token=access_token)
        else:
            abort(401)


@planner_blp.route("/planner_logout")
class PlannerLogout(MethodView):

    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        current_app.jwt_redis_blocklist.set(jti, "", ex=current_app.jwt_exp)
        return jsonify(msg=f"Access token expired.")


@planner_blp.route("/user:<int:user_id>/my_events")
class MyEvents(MethodView):

    @jwt_required()
    @planner_blp.response(200, EventSchema(many=True))
    def get(self, user_id):
        user = get_jwt()
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account to delete.")
        if user["sub"] != user_id:
            abort(404, message="Not found.")
        results = None
        user = None
        try:
            user = db.session.execute(db.select(PlannerModel).where(PlannerModel.id==user_id)).scalar_one()
        except SQLAlchemyError:
            abort(404, message="User not found")
        return user.events

    