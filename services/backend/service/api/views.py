from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, views
from rest_framework.exceptions import PermissionDenied

from apps.call_center.db.models import Practice
from apps.email.tasks.daily_updates_emailing import (
    CreateDailyUpdatesEmailEventsPeriodicTask,
)
from apps.sms.tasks.sms_aggregating import (
    SMSEventCreationTask,
    SMSEventCreationSubtaskLaunchPeriodicTask,
)

User = get_user_model()


class DBHealthCheckView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            User.objects.first()
        except DatabaseError:
            return JsonResponse({'status': 'error'})
        return JsonResponse({})


class HealthCheckView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        return JsonResponse({})


class APIInfoView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        api_info = {
            'current_version': 'v1',
            'supported_versions': [
                'v1',
            ],
        }
        return JsonResponse(api_info)


class SentryDebugView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        raise Exception('Sentry debug exception')

    def check_permissions(self, request):
        if not settings.DEBUG:
            raise PermissionDenied
        return super().check_permissions(request)


class SMSEventCreationTestView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'odu_id'

    def get(self, request, *args, **kwargs):
        practice = self.get_object(kwargs['odu_id'])
        SMSEventCreationTask().apply_async(kwargs={'practice_id': practice.odu_id})
        return JsonResponse({})

    def get_object(self, practice_id):
        return get_object_or_404(
            Practice, odu_id=practice_id, settings__is_sms_mailing_enabled=True
        )

    def check_permissions(self, request):
        return super().check_permissions(request)


class SMSEventCreationSubtaskLaunchTestView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        SMSEventCreationSubtaskLaunchPeriodicTask().apply_async()
        return JsonResponse({})

    def check_permissions(self, request):
        if not settings.DEBUG:
            raise PermissionDenied
        return super().check_permissions(request)


class DailyEmailUpdatesTestView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, *args, **kwargs):
        CreateDailyUpdatesEmailEventsPeriodicTask().apply_async()
        return JsonResponse({})

    def check_permissions(self, request):
        return super().check_permissions(request)
