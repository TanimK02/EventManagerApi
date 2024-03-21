from datetime import timedelta
import redis
from flask import Flask, request
from flask_smorest import Api, abort
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt
from models import PlannerModel, UserModel
from sqlalchemy.exc import SQLAlchemyError
from db import db
from resources.planner import planner_blp
from resources.user import user_blp

ACCESS_EXPIRES = timedelta(hours=2)


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Blog REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.1.0"
    app.config["OPENAPI_URL_PREFIX"] = "/"

    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = "123123123"
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    app.jwt_exp = ACCESS_EXPIRES
    app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
    jwt = JWTManager(app)
    
    app.jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = app.jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            if jwt_data["Model"] == "Planner":
                return db.session.execute(db.select(PlannerModel).where(PlannerModel.id==identity)).scalar_one()
            elif jwt_data["Model"] == "User":
                return db.session.execute(db.select(UserModel).where(UserModel.id==identity)).scalar_one()
        except SQLAlchemyError:
            abort(400, message="User doesn't exist")
        
    
    
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()

    api = Api(app)
    api.register_blueprint(planner_blp)
    api.register_blueprint(user_blp)
    
    
    return app