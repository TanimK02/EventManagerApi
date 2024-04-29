from celery import Celery

app = Celery('Event_Scheduler', broker = 'amqp://', include=['Event_Scheduler.tasks', 'Event_Scheduler.db'])

app.conf.beat_schedule = {
    'send-mail every day': {
        'task': 'tasks.send_mail',
        'schedule': 30.0
    }
}