from django.conf import settings
from django.urls import include, path

from .docs import urlpatterns as docs_urlpatterns
from .v1.urls import urlpatterns as v1_urlpatterns
from .views import (
    APIInfoView,
    DBHealthCheckView,
    HealthCheckView,
    SMSEventCreationTestView,
    SMSEventCreationSubtaskLaunchTestView,
    DailyEmailUpdatesTestView,
    SentryDebugView,
)

urlpatterns = [
    path('', APIInfoView.as_view()),
    path('v1/', include(v1_urlpatterns)),
    path('health-check/', HealthCheckView.as_view()),
    path('db-health-check/', DBHealthCheckView.as_view()),
    path('sms-event-creation/<str:odu_id>', SMSEventCreationTestView.as_view()),
    path('daily-email-updates', DailyEmailUpdatesTestView.as_view()),
]

if settings.DEBUG:
    urlpatterns.extend([
        path('sentry-debug/', SentryDebugView.as_view()),
        path('docs/', include(docs_urlpatterns)),
        path('sms-event-creation-subtask-launch', SMSEventCreationSubtaskLaunchTestView.as_view()),
    ])
