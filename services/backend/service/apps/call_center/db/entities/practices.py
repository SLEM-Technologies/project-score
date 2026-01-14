from django.core import validators
from django.db import models
from django.db.models import Q

from libs.db.base_models import BaseModel
from apps.base.constants.errors import SystemMessageEnum
from apps.call_center.db.base_models import AbstractCallCenterModel
from apps.call_center.db.validators import validate_is_digit
from apps.sms.consts import MAX_EXPIRY_PERIOD_IN_YEARS, MIN_EXPIRY_PERIOD_IN_WEEKS

from .servers import Server


class Practice(AbstractCallCenterModel):
    odu_id = models.CharField(primary_key=True, db_column='PRACTICE_ODU_ID')
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='practices',
    )
    name = models.CharField(max_length=256, null=True, db_column='NAME')
    address_1 = models.CharField(null=True, db_column='ADDRESS_1')
    address_2 = models.CharField(null=True, db_column='ADDRESS_2')
    city = models.CharField(null=True, db_column='CITY')
    state = models.CharField(null=True, db_column='STATE')
    country = models.CharField(null=True, db_column='COUNTRY')
    zip_code = models.CharField(null=True, db_column='ZIP')
    phone = models.CharField(max_length=256, null=True, db_column='PHONE')
    has_pims_connection = models.BooleanField(
        null=True, db_column='HAS_PIMS_CONNECTION'
    )
    pims = models.CharField(null=True, db_column='PIMS')
    latest_extractor_updated = models.DateTimeField(
        null=True, db_column='LATEST_EXTRACTOR_UPDATED_AT_UTC'
    )
    latest_transaction = models.DateTimeField(null=True, db_column='LATEST_TRANSACTION')
    server_import_finished = models.DateTimeField(
        null=True, db_column='SERVER_IMPORT_FINISHED_AT_UTC'
    )
    practice_updated_at = models.DateTimeField(
        null=True, db_column='PRACTICE_UPDATED_AT_UTC'
    )

    data_source = models.CharField(max_length=255, null=True, db_column='DATA_SOURCE')
    is_archived = models.BooleanField(default=False, db_column='APP_IS_ARCHIVED')

    def __str__(self) -> str | None:
        return self.name


class Question(BaseModel):
    text = models.CharField(max_length=255)

    class Meta:
        ordering = ('text',)

    def __str__(self) -> str:
        return self.text


class Answer(BaseModel):
    practice = models.ForeignKey(
        Practice, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        Question, on_delete=models.PROTECT, related_name='answers'
    )
    text = models.CharField(verbose_name='Answer text', max_length=4000)

    class Meta:
        ordering = ('text',)
        constraints = (
            models.UniqueConstraint(
                fields=('practice', 'question'), name='unique_practice_question'
            ),
        )

    def __str__(self) -> str:
        return self.text if len(self.text) <= 100 else self.text[:100] + '...'


class PracticeSettings(BaseModel):
    practice = models.OneToOneField(
        Practice, on_delete=models.CASCADE, related_name='settings'
    )
    is_sms_mailing_enabled = models.BooleanField(
        verbose_name='SMS Mailing',
        default=False,
        help_text='Activates sending SMS reminders to clients.',
    )
    is_email_updates_enabled = models.BooleanField(
        verbose_name='Sending updates by email',
        default=False,
        help_text='Activates sending Excel files with data updates.',
    )
    sms_senders_phone = models.CharField(
        verbose_name='Sender\'s phone number',
        max_length=10,
        blank=True,
        validators=[validators.MinLengthValidator(limit_value=10), validate_is_digit],
        help_text='Can only contain 10 digits.',
    )
    sms_scheduler = models.CharField(
        verbose_name='Scheduler name in SMS', max_length=100, blank=True
    )
    sms_practice_name = models.CharField(
        verbose_name='Practice name in SMS', max_length=100, blank=True
    )
    sms_phone = models.CharField(
        verbose_name='Phone number in SMS',
        max_length=20,
        blank=True,
    )
    sms_link = models.CharField(verbose_name='Link in SMS', max_length=150, blank=True)
    email = models.EmailField(
        verbose_name='Practice contact email',
        blank=True,
    )
    launch_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            'Date when the SMS aggregation logic will check reminders '
            f'with date_due between {MIN_EXPIRY_PERIOD_IN_WEEKS} weeks and {MAX_EXPIRY_PERIOD_IN_YEARS} years.'
        ),
    )
    start_date_for_launch = models.DateField(
        null=True,
        blank=True,
        help_text=(
            'The date that the SMS aggregation logic will use when generating SMS, '
            'i.e. defines the right boundary of the date range. If you set only this date for the left boundary, '
            f'the default logic will be used ({MIN_EXPIRY_PERIOD_IN_WEEKS} weeks ago).'
        )
    )
    end_date_for_launch = models.DateField(
        null=True,
        blank=True,
        help_text=(
            'The date that the SMS aggregation logic will use when generating SMS, '
            'i.e. defines the left boundary of the date range.'
        )
    )
    scheduler_email = models.EmailField(blank=True)
    rdo_name = models.CharField(max_length=100, blank=True)
    rdo_email = models.EmailField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (
                        (
                            Q(sms_senders_phone='')
                            | Q(sms_scheduler='')
                            | Q(sms_practice_name='')
                            | Q(sms_link='')
                        )
                        & Q(is_sms_mailing_enabled=False)
                    )
                    | (
                        ~Q(sms_senders_phone='')
                        & ~Q(sms_scheduler='')
                        & ~Q(sms_practice_name='')
                        & ~Q(sms_link='')
                        & (
                            Q(is_sms_mailing_enabled=False)
                            | Q(is_sms_mailing_enabled=True)
                        )
                    )
                ),
                name='check_sms_fields_condition',
                violation_error_message=SystemMessageEnum.X0005.value.detail,
            ),
            models.CheckConstraint(
                check=(
                    (Q(email='') & Q(is_email_updates_enabled=False))
                    | (
                        ~Q(email='')
                        & (
                            Q(is_email_updates_enabled=False)
                            | Q(is_email_updates_enabled=True)
                        )
                    )
                ),
                name='check_email_fields_condition',
                violation_error_message=SystemMessageEnum.X0007.value.detail,
            ),
        ]
