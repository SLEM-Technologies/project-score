from django.db import models

from libs.db.base_models import BaseModel
from apps.call_center.db.base_models import BaseCallCenterModel

from .servers import Server


class Patient(BaseCallCenterModel):
    odu_id = models.CharField(primary_key=True, db_column='PATIENT_ODU_ID')
    server = models.ForeignKey(
        Server,
        on_delete=models.PROTECT,
        null=True,
        db_column='SERVER_ODU_ID',
        related_name='patients',
    )
    birth_date = models.DateField(null=True, db_column='BIRTH_DATE')
    death_date = models.DateField(null=True, db_column='DEATH_DATE')
    euthanasia_date = models.DateField(null=True, db_column='EUTHANASIA_DATE')
    pims_entered_date = models.DateField(null=True, db_column='PIMS_ENTERED_DATE')
    earliest_medical_service_date = models.DateField(
        null=True, db_column='EARLIEST_MEDICAL_SERVICE_DATE'
    )
    name = models.CharField(null=True, db_column='NAME')
    pims_id = models.CharField(null=True, db_column='PIMS_ID')
    species = models.CharField(null=True, db_column='SPECIES')
    species_description = models.CharField(null=True, db_column='SPECIES_DESCRIPTION')
    breed = models.CharField(null=True, db_column='BREED')
    breed_description = models.CharField(null=True, db_column='BREED_DESCRIPTION')
    color = models.CharField(null=True, db_column='COLOR')
    color_description = models.CharField(null=True, db_column='COLOR_DESCRIPTION')
    gender = models.CharField(null=True, db_column='GENDER')
    gender_description = models.CharField(null=True, db_column='GENDER_DESCRIPTION')
    weight = models.CharField(null=True, db_column='WEIGHT')
    weight_units = models.CharField(null=True, db_column='WEIGHT_UNITS')
    pims_is_deleted = models.BooleanField(null=True, db_column='PIMS_IS_DELETED')
    odu_is_deleted = models.CharField(null=True, db_column='ODU_IS_DELETED')
    pims_is_deceased = models.BooleanField(null=True, db_column='PIMS_IS_DECEASED')
    is_deceased = models.BooleanField(null=True, db_column='IS_DECEASED')
    pims_is_inactive = models.BooleanField(null=True, db_column='PIMS_IS_INACTIVE')
    is_safe_to_contact = models.BooleanField(null=True, db_column='IS_SAFE_TO_CONTACT')
    pims_has_suspended_reminders = models.BooleanField(
        null=True, db_column='PIMS_HAS_SUSPENDED_REMINDERS'
    )
    is_online = models.BooleanField(null=True, db_column='IS_ONLINE')
    is_inclinic = models.BooleanField(null=True, db_column='IS_INCLINIC')
    new_date_updated_at = models.DateTimeField(
        null=True, db_column='IS_NEW_DATE_UPDATED_AT_UTC'
    )
    latest_medical_service_date = models.DateField(
        null=True, db_column='LATEST_MEDICAL_SERVICE_DATE'
    )
    patient_new_date = models.DateField(
        null=True, db_column='PATIENT_IS_NEW_DATE'
    )
    patient_record_updated_at = models.DateTimeField(
        null=True, db_column='PATIENT_RECORD_UPDATED_AT_UTC'
    )

    # custom fields
    outcome = models.CharField(max_length=255, null=True, db_column='APP_OUTCOME')
    opt_out = models.BooleanField(null=True, db_column='APP_OPT_OUT')
    comment = models.CharField(max_length=1000, null=True, db_column='APP_COMMENT')
    outcome_at = models.DateTimeField(null=True, db_column='APP_OUTCOME_AT', default=None)

    def __str__(self) -> str | None:
        return self.name


class Outcome(BaseModel):
    text = models.CharField(max_length=255)

    class Meta:
        ordering = ('text',)

    def __str__(self) -> str:
        return self.text
