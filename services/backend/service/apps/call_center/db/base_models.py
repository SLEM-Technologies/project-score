from django.db import models


class AbstractCallCenterModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_column='APP_CREATED_AT')
    updated_at = models.DateTimeField(auto_now=True, null=True, db_column='APP_UPDATED_AT')

    class Meta:
        abstract = True


class BaseCallCenterModel(AbstractCallCenterModel):
    odu_created_at = models.DateTimeField(null=True, db_column='ODU_CREATED_AT_UTC')
    odu_updated_at = models.DateTimeField(null=True, db_column='ODU_UPDATED_AT_UTC')
    extractor_created_at = models.DateTimeField(
        null=True, db_column='EXTRACTOR_CREATED_AT_UTC'
    )
    extractor_updated_at = models.DateTimeField(
        null=True, db_column='EXTRACTOR_UPDATED_AT_UTC'
    )
    extractor_removed_at = models.DateTimeField(
        null=True, db_column='EXTRACTOR_REMOVED_AT_UTC'
    )
    data_source = models.CharField(max_length=255, null=True, db_column='DATA_SOURCE')

    class Meta:
        abstract = True
