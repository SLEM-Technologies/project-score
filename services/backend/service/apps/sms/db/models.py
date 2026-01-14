from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django_jsonform.models.fields import ArrayField

from libs.db.base_models import BaseModel
from apps.call_center.db.entities.clients import Client
from apps.call_center.db.entities.practices import Practice
from apps.sms.consts import SMS_TEMPLATES_CACHE_KEY, SMSEventStatus, SMSHistoryStatus


class SMSEvent(BaseModel):
    send_at = models.DateTimeField(default=timezone.now)
    context = models.JSONField()
    status = models.CharField(
        max_length=32,
        choices=SMSEventStatus.choices,
        default=SMSEventStatus.PENDING.value,
    )

    class Meta:
        indexes = [
            models.Index(fields=['send_at', 'status'], name='send_at_status_idx'),
        ]


class SMSHistory(BaseModel):
    practice = models.ForeignKey(
        Practice, on_delete=models.SET_NULL, null=True, related_name='sms_history'
    )
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, related_name='sms_history'
    )
    event_context = models.JSONField()
    sent_at = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=32,
        choices=SMSHistoryStatus.choices,
        default=SMSHistoryStatus.PENDING.value,
    )
    response = models.JSONField(null=True)
    error_message = models.TextField(null=True)
    is_followed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['sent_at'], name='sent_at_idx'),
        ]


class SMSTemplate(BaseModel):
    key_words = ArrayField(
        models.CharField(max_length=64),
    )
    template = models.TextField()

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        cache.delete(SMS_TEMPLATES_CACHE_KEY)
        return result

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete(SMS_TEMPLATES_CACHE_KEY)
        return result

    @classmethod
    def get_values_dict(cls):
        cached_data = cache.get(SMS_TEMPLATES_CACHE_KEY)
        if cached_data is not None:
            return cached_data
        templates = cls.objects.all()
        templates_dict = {
            tuple(key_word.lower() for key_word in obj.key_words): obj.template
            for obj in templates
        }
        cache.set(SMS_TEMPLATES_CACHE_KEY, templates_dict, timeout=1800)  # cache for half an hour
        return templates_dict

    class Meta:
        verbose_name = 'SMS template'
        verbose_name_plural = 'SMS templates'
