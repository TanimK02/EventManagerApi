from datetime import date
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func
from models import EventModel, user_events, RatingsModel, ReviewModel
from schemas import ReviewSchema, EventResponseSchema
from db import db
import ssl
import smtplib
from email.message import EmailMessage

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
        if event.published != 1:
            abort(404, message="Event not found.")
        check = db.session.execute(db.select(user_events).where(user_events.c.user==user["sub"]).where(user_events.c.event==event.id)).first()
        print(check)
        if check:
            abort(400, message="Already registered.")
        
        try:
            event.registered.append(user_data)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while registering for event")

        try:
            email_sender = current_app.config["EMAIL"]
            email_pass = current_app.config["PASSWORD"]
            email_receiver = current_user.email

            subject = f"Registered for {event.title}"
            body = f"You successfully registered for {event.title}. Don't forget its on {event.date}. Don't miss it."
            em = EmailMessage()
            em["From"] = email_sender
            em["To"] = email_receiver
            em["Subject"] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_pass)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
        except:
            abort(400, message="Something went wrong with the confirmation email.")

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
        if event.published != 1:
            abort(404, message="Event not found.")
        check = db.session.execute(db.select(user_events).where(user_events.c.user==user["sub"]).where(user_events.c.event==event.id)).first()
        print(check)
        if not check:
            abort(400, message="Already not registered.")
        
        try:
            event.registered.remove(user_data)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while unregistering for event")

        try:
            email_sender = current_app.config["EMAIL"]
            email_pass = current_app.config["PASSWORD"]
            email_receiver = current_user.email

            subject = f"Registered for {event.title}"
            body = f"You have been unregistered from {event.title}."
            em = EmailMessage()
            em["From"] = email_sender
            em["To"] = email_receiver
            em["Subject"] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_pass)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
        except:
            abort(400, message="Something went wrong with the confirmation email.")

        return {"message": "Unregistered"}
    

@blp.route("/leave_review/<int:event_id>")
class LeaveReview(MethodView):

    @jwt_required()
    @blp.arguments(ReviewSchema)
    def post(self, review_data, event_id):
        user = get_jwt()
        rate = review_data.pop("rate")
        event = db.get_or_404(EventModel, event_id)
        if event.published != 1:
            abort(404, message="Event not found.")
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
            review.comment=review_data["comment"]
            review.rate = rate
            review.updated_at = date.today()
        else:
            review = ReviewModel(**review_data)
            review.event_id = event_id
            review.rate = rate
            review.creator_id = user["sub"]
            review.created_at = date.today()
        review.rating.append(rating)
        try:
            db.session.add(review)
            db.session.commit()
        except SQLAlchemyError:
            abort(400, message="Something went wrong while processing review")
        reset_rating(event_id=event_id)
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
        reset_rating(event_id=event_id)
        return {"message": "Review deleted."}
    

@blp.route("/rating/<int:event_id>/<int:rate>")
class LeaveRate(MethodView):

    @jwt_required()
    def post(self, event_id, rate):
        user = get_jwt()
        rating = None
        event = db.get_or_404(EventModel, event_id)
        if event.published != 1:
            abort(404, message="Event not found.")
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
        reset_rating(event_id=event_id)
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
        reset_rating(event_id=event_id)
        return {"message": "Deleted rating and review if left there."}
    

@blp.route("/view_reviews/<int:event_id>")
class ViewReviews(MethodView):

    @blp.response(200, ReviewSchema(many=True))
    def get(self, event_id):
        event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id)).scalar_one()
        return event.reviews
    

@blp.route("/events")
class ViewEvents(MethodView):

    @blp.response(200, EventResponseSchema(many=True))
    def get(self):
        return db.session.execute(db.select(EventModel).where(EventModel.published==1).order_by(desc(EventModel.published_at))).scalars()
    

@blp.route("/event/<int:event_id>")
class ViewSingleEvent(MethodView):

    @blp.response(200, EventResponseSchema)
    def get(self, event_id):
        event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id).where(EventModel.published_at!=None)).scalar_one_or_none()
        if not event or event.published != 1:
            abort(404, message="Does not exist.")
        return event


def reset_rating(event_id):
    event = db.session.execute(db.select(EventModel).where(EventModel.id==event_id)).scalar_one_or_none()
    if event:
        ratings = db.session.execute(db.select(func.avg(RatingsModel.rating)).where(RatingsModel.event==event_id)).all()
        if ratings[0][0]:
            event.rating = ratings[0][0]
        else:
            event.rating = 0
    db.session.commit()
        
    