import datetime
import socket

from decouple import config

from settings.settings import main as main_settings
from libs.celery import consts as celery_consts

broker_url = main_settings.CACHE_STORAGE
accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
task_always_eager = config('CELERY_TASK_ALWAYS_EAGER', cast=bool, default=False)
task_eager_propagates = config('CELERY_TASK_EAGER_PROPAGATES', cast=bool, default=False)
result_extended = config('CELERY_RESULT_EXTENDED', cast=bool, default=True)
result_backend = 'django-db'
result_expires = datetime.timedelta(days=celery_consts.RESULT_BACKEND_EXPIRES_DAYS)
cache_backend = 'django-cache'
broker_connection_retry_on_startup = True
broker_transport_options = {
    'socket_keepalive': True,
    'socket_keepalive_options': {
        # time (in seconds) the connection needs to remain idle
        # before TCP starts sending keepalive probes
        socket.TCP_KEEPIDLE: 540,

        # time (in seconds) between individual keepalive probes
        socket.TCP_KEEPINTVL: 10,

        # maximum number of keepalive probes TCP should send
        # before dropping the connection
        socket.TCP_KEEPCNT: 5,
    },
}

# Kill all long-running tasks with late acknowledgment enabled
# (sms.event_creation) on connection loss.
worker_cancel_long_running_tasks_on_connection_loss = True

task_default_queue = celery_consts.CeleryQueue.DEFAULT.value
imports = (
    'apps.sms.tasks.sms_sending',
    'apps.sms.tasks.sms_aggregating',
    'apps.email.tasks.daily_updates_emailing',
)
task_routes = {
    'apps.sms.tasks.sms_sending.SMSEventPeriodicTask': {
        'queue': celery_consts.CeleryQueue.DEFAULT.value
    },
    'apps.sms.tasks.sms_sending.SMSSendingTask': {
        'queue': celery_consts.CeleryQueue.SMS.value
    },
    'apps.sms.tasks.sms_aggregating.SMSEventCreationSubtaskLaunchPeriodicTask': {
        'queue': celery_consts.CeleryQueue.DEFAULT.value
    },
    'apps.sms.tasks.sms_aggregating.SMSEventCreationTask': {
        'queue': celery_consts.CeleryQueue.DEFAULT.value
    },
    'apps.email.tasks.daily_updates_emailing.CreateDailyUpdatesEmailEventsPeriodicTask': {
        'queue': celery_consts.CeleryQueue.EMAIL.value
    },
    'apps.email.tasks.daily_updates_emailing.SendDailyUpdatesEmailTask': {
        'queue': celery_consts.CeleryQueue.EMAIL.value
    },
}
beat_schedule = {
    'call_sms_event_every_one_minute': {
        'task': 'sms_event_manager',
        'schedule': celery_consts.EVERY_MINUTE_ON_WEEKDAYS_FROM_15_TO_23_HOURS,
        'options': {
            'queue': celery_consts.CeleryQueue.DEFAULT.value,
        },
    },
    'sms_event_creation_subtask_launch_daily_at_1am': {
        'task': 'sms.event_creation_subtask_launch',
        'schedule': celery_consts.DAILY_AT_1330PM_UTC,
        'options': {
            'queue': celery_consts.CeleryQueue.DEFAULT.value,
        },
    },
    'daily_updates_emailing_at_1pm': {
        'task': 'daily_updates_manager',
        'schedule': celery_consts.DAILY_AT_1PM_UTC,
        'options': {
            'queue': celery_consts.CeleryQueue.EMAIL.value,
        },
    },
}
