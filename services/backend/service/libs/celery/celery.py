from decouple import config

from celery import Celery


app = Celery('vetsuccess')
app.config_from_object(
    config('DJANGO_SETTINGS_MODULE'),
    force=True,
)

app.autodiscover_tasks()
