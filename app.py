from flask import Flask
from flask_smorest import Api

app = Flask(__name__)

# def create_app():
#     app = Flask(__name__)
#     app.config["API_TITLE"] = "Blog REST API"
#     app.config["API_VERSION"] = "v1"
#     app.config["OPENAPI_VERSION"] = "3.1.0"
#     app.config["OPENAPI_URL_PREFIX"] = "/"

#     app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
#     app.config[
#         "OPENAPI_SWAGGER_UI_URL"
#     ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
#     app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Peanutbutterseats123!@host.docker.internal:5432/blog_api"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     app.config["PROPAGATE_EXCEPTIONS"] = True
#     app.config["SESSION_TYPE"] = "filesystem"
#     app.config.update(
#     SESSION_COOKIE_SECURE=True,
#     SESSION_COOKIE_HTTPONLY=True,
#     SESSION_COOKIE_SAMESITE='Lax',
# )

#     api = Api(app)


#     return app