from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from apps.email.consts import UpdatesEmailEventStatus
from libs.db.base_models import BaseModel

from apps.call_center.db.entities.practices import Practice


class UpdatesEmailEvent(BaseModel):
    practice = models.ForeignKey(Practice, null=True, on_delete=models.SET_NULL)
    file_paths = ArrayField(
        models.CharField(max_length=1000),
    )
    sent_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=32,
        choices=UpdatesEmailEventStatus.choices,
        default=UpdatesEmailEventStatus.PENDING.value,
    )
    error_message = models.TextField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['sent_date'], name='sent_date_files_event_idx'),
            models.Index(fields=['status'], name='status_files_event_idx'),
        ]
