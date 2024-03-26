from datetime import date
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from sqlalchemy.orm import noload
from models import EventModel
from schemas import EventSchema
from db import db

blp = Blueprint("Events", "events", description = "Operations on events for the planners")

@blp.route("/create_event")
class Event(MethodView):
    @jwt_required()
    @blp.arguments(EventSchema)
    @blp.response(201, EventSchema)
    def post(self, post_data):
        user = current_user
        model = get_jwt()
        if model["Model"] != "Planner":
            abort(401, message="Need Planner account to be able to make events")
        post_data["creator_id"] = user.id
        post_data["creator"] = user.name
        try:
            post = EventModel(**post_data)
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="An error occured while processing the post.")
        
        return post
    

@blp.route("/delete_event/<int:event_id>")
class DeleteEvent(MethodView):
    @jwt_required()
    def delete(self, event_id):
        user = get_jwt()
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account to delete and wrong id.")
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id)).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        if event.creator_id != get_jwt_identity():
            abort(401, message="Not authorized to delete this event.")

        db.session.delete(event)
        db.session.commit()

        return {"message": "Deleted event"}, 200