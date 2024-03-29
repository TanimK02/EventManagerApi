from datetime import date
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from models import EventModel, PlannerModel
from schemas import EventSchema, EventResponseSchema, EventEditSchema, EditorSchema
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
        post_data["created_at"] = date.today()
        try:
            post = EventModel(**post_data)
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="An error occured while processing the event.")
        
        return post
    

@blp.route("/my_event/<int:event_id>")
class ViewEvent(MethodView):
    
    @jwt_required()
    @blp.response(200, EventResponseSchema)
    def get(self, event_id):
        event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==get_jwt_identity()).order_by(desc(EventModel.created_at))).scalar_one_or_none()
        if not event:
            abort(404, message="Does not exist.")
        return event


@blp.route("/delete_event/<int:event_id>")
class DeleteEvent(MethodView):
    @jwt_required()
    def delete(self, event_id):
        user = get_jwt()
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account to delete.")
        event = None
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==user["sub"])).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        if event:
            db.session.delete(event)
            db.session.commit()
        else:
            abort(404, message="Event not found.")
        return {"message": "Deleted event"}, 200
    

@blp.route("/edit_event/<int:event_id>")
class EditEvent(MethodView):

    @jwt_required()
    @blp.arguments(EventEditSchema)
    @blp.response(200, EventSchema)
    def put(self, event_data, event_id):
        user = get_jwt()
        event = None
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account to edit.")
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==user["sub"])).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        
        if event:
            try:
                event.title = event_data.get("title",event.title)
                event.description = event_data.get("description", event.description)
                event.price = event_data.get("price", event.price)
                event.max_attendants = event_data.get("max_attendants", event.max_attendants)
                event.updated_at = date.today()
                db.session.add(event)
                db.session.commit()
            except SQLAlchemyError:
                abort(400, message="An error occured while processing the update.")
        else:
            abort(404, message="Event not found")

        return event


@blp.route("/add_editors/<int:event_id>")
class AddEditors(MethodView):

    @jwt_required()
    @blp.arguments(EditorSchema)
    @blp.response(200, EventSchema)
    def put(self, editors, event_id):
        user = get_jwt()
        event = None
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account.")
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==user["sub"])).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        
        if event:
            try:
                for i in editors["editors"]:
                    editor = db.session.execute(db.select(PlannerModel).where(PlannerModel.username==i)).scalar_one()
                    event.editors.append(editor)
                    db.session.add(event)
                    db.session.commit()
            except SQLAlchemyError:
                abort(400, message="An error occured while processing the update.")
        else:
            abort(404, message="Event not found")

        return event
    

@blp.route("/remove_editors/<int:event_id>")
class RemoveEditors(MethodView):

    @jwt_required()
    @blp.arguments(EditorSchema)
    @blp.response(200, EventSchema)
    def delete(self, editors, event_id):
        user = get_jwt()
        event = None
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account.")
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==user["sub"])).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        
        if event:
            try:
                for i in editors["editors"]:
                    editor = db.session.execute(db.select(PlannerModel).where(PlannerModel.username==i)).scalar_one()
                    event.editors.remove(editor)
                    db.session.commit()
            except SQLAlchemyError:
                abort(400, message="An error occured while processing the update.")
        else:
            abort(404, message="Event not found")

        return event


@blp.route("/publish_event/<int:event_id>")
class PublishEvent(MethodView):

    @jwt_required()
    def put(self, event_id):
        user = get_jwt()
        event = None
        if user["Model"] != "Planner":
            abort(401, message="Need a planner account.")
        try:
            event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.creator_id==user["sub"])).scalar_one()
        except SQLAlchemyError:
            abort(404, message="Event not found.")
        
        if event:
            try:
                event.published_at = date.today()
                event.published = 1
                db.session.add(event)
                db.session.commit()
            except SQLAlchemyError:
                abort(400, message="An error occured while processing the update.")
        else:
            abort(404, message="Event not found")
        
        return {"message": "published"}