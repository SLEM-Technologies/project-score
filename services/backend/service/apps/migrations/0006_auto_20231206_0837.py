# stub instead of migrating data. the data is actually migrated
# in migration 0028_remove_and_add_outcomes.py

from django.db import migrations


def add_outcomes(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_outcome'),
    ]

    operations = [
        migrations.RunPython(add_outcomes, reverse_code=migrations.RunPython.noop),
    ]
