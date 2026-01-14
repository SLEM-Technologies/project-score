from django.db import models

from apps.call_center.consts import ReminderStatus
from apps.call_center.db.base_models import BaseCallCenterModel
from apps.call_center.db.models import Client, Patient, Practice, Server
from apps.sms.db.models import SMSHistory


class Reminder(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='REMINDER_ODU_ID'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='reminders',
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='reminders',
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        null=True,
        db_column='PATIENT_ODU_ID',
        related_name='reminders',
    )
    practice = models.ForeignKey(
        Practice,
        on_delete=models.PROTECT,
        null=True,
        db_column='PRACTICE_ODU_ID',
        related_name='reminders',
    )
    division_odu_id = models.CharField(null=True, db_column='DIVISION_ODU_ID')
    date_due = models.DateField(null=True, db_column='DUE_DATE')
    description = models.CharField(null=True, db_column='DESCRIPTION')
    code = models.CharField(null=True, db_column='CATALOG_CODE')
    type = models.CharField(null=True, db_column='TYPE')
    catalog_odu_id = models.CharField(null=True, db_column='CATALOG_ODU_ID')

    # app fields for storing information related to SMS sending
    sms_status = models.CharField(
        max_length=30,
        null=True,
        choices=ReminderStatus.choices,
        db_column='APP_SMS_STATUS',
    )
    sms_history = models.ForeignKey(
        SMSHistory,
        on_delete=models.PROTECT,
        null=True,
        db_column='APP_SMS_HISTORY',
        related_name='reminders',
    )

    def __str__(self) -> str | None:
        return self.description

    class Meta:
        indexes = [
            models.Index(fields=['date_due'], name='date_due_idx'),
        ]


class Appointment(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='APPOINTMENT_ODU_ID'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='appointments',
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='appointments',
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        null=True,
        db_column='PATIENT_ODU_ID',
        related_name='appointments',
    )
    practice = models.ForeignKey(
        Practice,
        on_delete=models.PROTECT,
        null=True,
        db_column='PRACTICE_ODU_ID',
        related_name='appointments',
    )
    is_canceled_appointment = models.BooleanField(
        null=True, db_column='IS_CANCELED_APPOINTMENT'
    )
    resource_odu_id = models.CharField(
        max_length=511, null=True, db_column='RESOURCE_ODU_ID'
    )
    division_odu_id = models.CharField(
        max_length=255, null=True, db_column='DIVISION_ODU_ID'
    )
    pims_source = models.CharField(max_length=255, null=True, db_column='PIMS_SOURCE')
    pims_reason = models.TextField(null=True, db_column='PIMS_REASON')
    pims_status = models.CharField(max_length=255, null=True, db_column='PIMS_STATUS')
    pims_schedule_type = models.CharField(
        max_length=255, null=True, db_column='PIMS_SCHEDULE_TYPE'
    )
    appointment_datetime = models.DateTimeField(null=True, db_column='APPOINTMENT_DATETIME')
    type = models.CharField(max_length=21, null=True, db_column='APPOINTMENT_TYPE')
    notes = models.TextField(null=True, db_column='NOTES')
    duration = models.BigIntegerField(null=True, db_column='DURATION')

    def __str__(self) -> str:
        return self.odu_id
