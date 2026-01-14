from django.core import validators
from django.db import models
from django.db.models.functions import Upper

from apps.call_center.db.base_models import BaseCallCenterModel
from apps.call_center.db.validators import validate_is_digit

from .patients import Patient
from .servers import Server


class Client(BaseCallCenterModel):
    odu_id = models.CharField(primary_key=True, db_column='CLIENT_ODU_ID')
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='clients',
    )
    patients = models.ManyToManyField(
        Patient, through='apps.ClientPatientRelationship', related_name='clients'
    )
    pims_entered_date = models.DateField(null=True, db_column='PIMS_ENTERED_DATE')
    earliest_transaction_date = models.DateField(
        null=True, db_column='EARLIEST_TRANSACTION_DATE'
    )
    earliest_online_transaction_date = models.DateTimeField(
        null=True, db_column='EARLIEST_ONLINE_TRANSACTION_DATETIME'
    )
    is_new_date = models.DateField(null=True, db_column='CLIENT_IS_NEW_DATE')
    online_account_created = models.DateTimeField(
        null=True, db_column='ONLINE_ACCOUNT_CREATED_AT_UTC'
    )
    pims_id = models.CharField(null=True, db_column='PIMS_ID')
    pims_is_deleted = models.BooleanField(null=True, db_column='PIMS_IS_DELETED')
    pims_is_inactive = models.BooleanField(null=True, db_column='PIMS_IS_INACTIVE')
    pims_has_suspended_reminders = models.BooleanField(
        null=True, db_column='PIMS_HAS_SUSPENDED_REMINDERS'
    )
    first_name = models.CharField(
        max_length=255, null=True, db_column='CLIENT_FIRST_NAME'
    )
    last_name = models.CharField(
        max_length=255, null=True, db_column='CLIENT_LAST_NAME'
    )
    full_name = models.CharField(
        max_length=511, null=True, db_column='CLIENT_FULL_NAME'
    )
    is_online = models.BooleanField(null=True, db_column='IS_ONLINE')
    is_inclinic = models.BooleanField(null=True, db_column='IS_INCLINIC')
    new_date_updated_at = models.DateTimeField(
        null=True, db_column='IS_NEW_DATE_UPDATED_AT_UTC'
    )
    latest_transaction_date = models.DateField(
        null=True, db_column='LATEST_TRANSACTION_DATE'
    )
    client_record_updated_at = models.DateTimeField(
        null=True, db_column='CLIENT_RECORD_UPDATED_AT_UTC'
    )
    is_safe_contact = models.BooleanField(
        null=True, db_column='IS_SAFE_TO_CONTACT'
    )

    is_home_practice = models.BooleanField(null=True, db_column='IS_HOME_PRACTICE')

    def __str__(self) -> str | None:
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        self.full_name = f'{self.first_name} {self.last_name}'
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(
                Upper('full_name'),
                name='upper_full_name_idx'
            ),
            models.Index(
                Upper('odu_id'),
                name='upper_odu_id_idx'
            ),
        ]


class ClientPatientRelationship(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='CLIENT_PATIENT_RELATIONSHIP_ODU_ID'
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='relationships',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='relationships',
    )
    patient = models.ForeignKey(
        to='apps.Patient',
        on_delete=models.PROTECT,
        null=True,
        db_column='PATIENT_ODU_ID',
        related_name='relationships',
    )
    start_date = models.DateField(null=True, db_column='START_DATE')
    end_date = models.DateField(null=True, db_column='END_DATE')
    is_primary = models.BooleanField(null=True, db_column='PIMS_IS_PRIMARY')
    percentage = models.FloatField(null=True, db_column='PERCENTAGE')
    relationship_type = models.CharField(null=True, db_column='RELATIONSHIP_TYPE')

    def __str__(self) -> str | None:
        return f'{self.client} - {self.patient}'


class Email(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='EMAIL_ODU_ID'
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='client_emails',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='emails',
    )
    type = models.CharField(null=True, db_column='EMAIL_TYPE')
    address = models.EmailField(unique=False, null=True, db_column='ADDRESS')
    is_primary = models.BooleanField(null=True, db_column='IS_PRIMARY')

    def __str__(self) -> str | None:
        return self.address

    class Meta:
        indexes = [
            models.Index(
                Upper('address'),
                'is_primary',
                'extractor_removed_at',
                name='filter_by_email_idx'
            ),
        ]


class Phone(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='PHONE_ODU_ID'
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='client_phones',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='phones',
    )
    number = models.CharField(null=True, db_column='NUMBER')
    type = models.CharField(null=True, db_column='PHONE_TYPE')
    is_primary = models.BooleanField(null=True, db_column='IS_PRIMARY')

    # app field for storing cleared numbers
    app_number = models.CharField(
        max_length=10,
        null=True,
        db_column='APP_NUMBER',
        validators=[validators.MinLengthValidator(limit_value=10), validate_is_digit],
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['app_number', 'is_primary', 'extractor_removed_at'],
                name='filter_by_phone_idx'
            ),
        ]

    def __str__(self) -> str | None:
        return self.number

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        self.number = self.app_number
        return super().save(force_insert, force_update, using, update_fields)


class Address(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='ADDRESS_ODU_ID'
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='client_addresses',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        null=True,
        db_column='CLIENT_ODU_ID',
        related_name='addresses',
    )
    line_1 = models.CharField(null=True, db_column='ADDRESS_1')
    line_2 = models.CharField(null=True, db_column='ADDRESS_2')
    city = models.CharField(null=True, db_column='CITY')
    state = models.CharField(null=True, db_column='STATE')
    postal_code = models.CharField(null=True, db_column='POSTAL_CODE')
    type = models.CharField(null=True, db_column='ADDRESS_TYPE')
    is_primary = models.BooleanField(null=True, db_column='IS_PRIMARY')

    def __str__(self) -> str | None:
        return f'{self.line_1}, {self.city}, {self.state} {self.postal_code}'
