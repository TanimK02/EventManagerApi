from datetime import date
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, current_user, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from models import EventModel, user_events, RatingsModel, ReviewModel
from schemas import ReviewSchema
from db import db


blp = Blueprint("User_Events", "user_events", description="User operations on events")


@blp.route("/register_event/<int:event_id>")
class RegisterEvent(MethodView):

    @jwt_required()
    def post(self, event_id):
        user = get_jwt()
        if user["Model"] != "User":
            abort(400, message="Need account to register")
        user_data = current_user
        event = db.get_or_404(EventModel, event_id)
        check = db.session.execute(db.select(user_events).where(user_events.c.user==user["sub"]).where(user_events.c.event==event.id)).first()
        print(check)
        if check:
            abort(400, message="Already registered.")
        
        try:
            event.registered.append(user_data)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while registering for event")

        return {"message": "Registered"}


@blp.route("/unregister_event/<int:event_id>")
class UnregisterEvent(MethodView):

    @jwt_required()
    def delete(self, event_id):
        user = get_jwt()
        if user["Model"] != "User":
            abort(400, message="Need account to unregister")
        user_data = current_user
        event = db.get_or_404(EventModel, event_id)
        check = db.session.execute(db.select(user_events).where(user_events.c.user==user["sub"]).where(user_events.c.event==event.id)).first()
        print(check)
        if not check:
            abort(400, message="Already not registered.")
        
        try:
            event.registered.remove(user_data)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while unregistering for event")

        return {"message": "Unregistered"}
    

@blp.route("/leave_review/<int:event_id")
class LeaveReview(MethodView):

    @jwt_required()
    @blp.arguments(ReviewSchema)
    def post(self, review_data, event_id):
        user = get_jwt()
        rate = review_data.pop("rating")
        rating = None
        if user["Model"] != "User":
            abort(400, message="Need account to leave review.")
        try:
            rating = (db.session.execute(db.select(RatingsModel).where(RatingsModel.event==event_id)
                                         .where(RatingsModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing review")
        if not rating:
            rating = RatingsModel()
            rating.rating = rate
            rating.creator_id = user["sub"]
            rating.event = event_id
        else:
            rating.rating = rate
        review = None
        try:
            review = (db.session.execute(db.select(ReviewModel).where(ReviewModel.event_id==event_id)
                                         .where(ReviewModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing review")
        if review:
            review.comment(review_data["comment"])
            review.rate = rate
        else:
            review = ReviewModel(**review_data)
            review.rate = rate
        review.rating.append(rating)
        try:
            db.session.add(review)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing review")
        
        return {"message": "Review added"}
    

@blp.route("/delete_review/<int:event_id>")
class DeleteReview(MethodView):

    @jwt_required()
    def delete(self, event_id):
        user = get_jwt()
        if user["Model"] != "User":
            abort(400, message="Need user account to delete review.")
        review = None
        try:
            review = (db.session.execute(db.select(ReviewModel).where(ReviewModel.event_id==event_id)
                                         .where(ReviewModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing review")
        if review:
            db.session.delete(review)
        else:
            abort(400, message="Review doesn't exist.")

        return {"message": "Review deleted."}
    

@blp.route("/rating/<int:event_id>/<int:rate>")
class LeaveRate(MethodView):

    @jwt_required()
    def post(self, event_id, rate):
        user = get_jwt()
        rating = None
        if user["Model"] != "User":
            abort(400, message="Need account to leave rating.")
        try:
            rating = (db.session.execute(db.select(RatingsModel).where(RatingsModel.event==event_id)
                                         .where(RatingsModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing the rating")
        if rating:
            rating.rating = rate
        else:
            rating = RatingsModel()
            rating.creator_id = user["sub"]
            rating.event = event_id
            rating.rating = rate
        review = None
        try:
            review = (db.session.execute(db.select(ReviewModel).where(ReviewModel.event_id==event_id)
                                         .where(ReviewModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing the rating")
        try:
            if review:
                review.rate = rate
                review.rating.append(rating)
            else:
                db.session.add(rating)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing the rating")
        
        return {"message": "Added rating."}


@blp.route("/delete_rating/<int:event_id>")
class DeleteRating(MethodView):

    @jwt_required()
    def delete(self, event_id):
        user = get_jwt()
        rating = None
        if user["Model"] != "User":
            abort(400, message="Need account to leave rating.")
        try:
            rating = (db.session.execute(db.select(RatingsModel).where(RatingsModel.event==event_id)
                                         .where(RatingsModel.creator_id==user["sub"])).scalar_one_or_none())
        except SQLAlchemyError:
            abort(400, message="Something went wrong while deleting the rating")
        if not rating:
            abort(400, message="No rating.")
        try:
            db.session.delete(rating)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while deleting the rating")
        return {"message": "Deleted rating and review if left there."}
    

@blp.route("/view_reviews/<int:event_id")
class ViewReviews(MethodView):

    def get(self):
        pass