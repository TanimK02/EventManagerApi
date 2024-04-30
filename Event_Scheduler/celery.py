from celery import Celery

app = Celery('Event_Scheduler', broker = 'amqp://host.docker.internal', include=['Event_Scheduler.tasks', 'Event_Scheduler.db'], broker_connection_retry_on_startup=True)

app.conf.beat_schedule = {
    'send-mail every day': {
        'task': 'tasks.send_mail',
        'schedule': 30.0
    }
}