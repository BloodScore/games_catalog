import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'games_catalog.settings')

app = Celery('games_catalog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'add-every-60-seconds': {
        'task': 'pages.tasks.celery_store_games',
        'schedule': settings.SCHEDULE,
        'args': (500,)
    },
}
