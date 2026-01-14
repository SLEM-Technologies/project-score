from django.db import models

from apps.call_center.db.base_models import AbstractCallCenterModel, BaseCallCenterModel


class Server(AbstractCallCenterModel):
    odu_id = models.BigIntegerField(primary_key=True, db_column='SERVER_ODU_ID')
    most_recent_pims_update = models.DateTimeField(
        null=True, db_column='SERVER_MOST_RECENT_PIMS_UPDATE'
    )
    latest_transaction = models.DateTimeField(
        null=True, db_column='SERVER_LATEST_TRANSACTION'
    )
    earliest_transaction = models.DateTimeField(
        null=True, db_column='SERVER_EARLIEST_TRANSACTION'
    )
    name = models.CharField(max_length=255, null=True, db_column='SERVER_NAME')
    pims = models.CharField(null=True, db_column='PIMS')
    address_1 = models.CharField(null=True, db_column='ADDRESS_1')
    address_2 = models.CharField(null=True, db_column='ADDRESS_2')
    city = models.CharField(null=True, db_column='CITY')
    state = models.CharField(null=True, db_column='STATE')
    country = models.CharField(null=True, db_column='COUNTRY')
    zip_code = models.CharField(null=True, db_column='ZIP')
    time_zone = models.CharField(max_length=255, null=True, db_column='TIME_ZONE')
    phone = models.CharField(max_length=255, null=True, db_column='PHONE')
    odu_created_at = models.DateTimeField(null=True, db_column='ODU_CREATED_AT_UTC')
    odu_updated_at = models.DateTimeField(null=True, db_column='ODU_UPDATED_AT_UTC')

    data_source = models.CharField(max_length=255, null=True, db_column='DATA_SOURCE')

    def __str__(self) -> str | None:
        return self.name


class SubServer(BaseCallCenterModel):
    odu_id = models.CharField(
        primary_key=True, max_length=255, db_column='SUBSERVER_ODU_ID'
    )
    server = models.ForeignKey(
        Server, on_delete=models.PROTECT, null=True, db_column='SERVER_ODU_ID'
    )
    display_name = models.CharField(null=True, db_column='DISPLAY_NAME')
    name = models.CharField(null=True, db_column='NAME')
    name = models.CharField(
        max_length=765, null=True, db_column='SUBSERVER_NAME'
    )
    time_zone = models.CharField(max_length=255, null=True, db_column='TIME_ZONE')

    def __str__(self) -> str | None:
        return self.display_name
