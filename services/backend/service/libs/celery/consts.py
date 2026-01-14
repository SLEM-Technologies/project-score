from django.db import models

from celery.schedules import crontab


EVERY_MINUTE_ON_WEEKDAYS_FROM_15_TO_23_HOURS = crontab(minute='*', hour='15-23', day_of_week='1-5')
DAILY_AT_1330PM_UTC = crontab(
    hour='13', minute='30'
)
DAILY_AT_1PM_UTC = crontab(
    hour='13', minute='0'
)
RESULT_BACKEND_EXPIRES_DAYS = 7


class CeleryQueue(models.TextChoices):
    SMS = 'sms'
    EMAIL = 'email'

    DEFAULT = 'low'
