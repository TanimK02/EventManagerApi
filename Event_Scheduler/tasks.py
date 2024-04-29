from celery import shared_task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from Event_Scheduler.db import Base
from Event_Scheduler.models import EventModel, UserModel
import ssl
import smtplib
from email.message import EmailMessage
from os import environ

# incase you wanna debug
# import logging

# from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)

# logging.basicConfig(level=logging.DEBUG)

@shared_task(name='tasks.send_mail')
def send_mail():

    engine = create_engine("sqlite:////tmp/test.db")
    Base.metadata.create_all(engine)

    list_amount = 100
    page = 0
    with Session(engine) as session:
        while True:
            events = session.execute(select(EventModel).where(EventModel.published==1).
                            order_by(EventModel.published_at).offset(page*list_amount).limit(list_amount)).scalars().all()
            print(events)
            if len(events) == 0:
                break
            for event in events:
                user_page = 0
                user_amount = 100
                while True:
                    users = session.execute(select(UserModel).join(EventModel.registered).
                                            where(EventModel.id==event.id).offset(user_page*user_amount).limit(user_amount)).scalars().all()
                    if len(users) == 0:
                        break
                    for user in users:
                        try:
                            email_sender = environ.get("EMAIL")
                            email_pass = environ.get("PASSWORD")
                            email_receiver = user.email
                            # logger.info(' email: %s password: %s ', email_sender, email_pass)
                            # incase you want to debug
                            subject = f"Reminder for {event.title}"
                            body = f"Don't forget to come to {event.title}. Its on {event.date}. Don't miss it."
                            em = EmailMessage()
                            em["From"] = email_sender
                            em["To"] = email_receiver
                            em["Subject"] = subject
                            em.set_content(body)

                            context = ssl.create_default_context()

                            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                                smtp.starttls()
                                # smtp.set_debuglevel(10)
                                # incase you wanna debug
                                smtp.login(email_sender, email_pass)
                                smtp.sendmail(email_sender, email_receiver, em.as_string())
                        except Exception as e:
                                print(f"Failed to send email to {email_receiver}: {str(e)}")
                    user_page += 1
            page += 1
        return {"message": "All events sent for."} 