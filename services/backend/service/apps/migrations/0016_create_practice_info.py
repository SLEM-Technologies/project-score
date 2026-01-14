# stub instead of migrating data. the data is actually migrated
# in migration 0029_add_practicesettings_info.py

from django.db import migrations


def create_practice_info(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0015_merge_20240116_1001'),
    ]

    operations = [
        migrations.RunPython(
            code=create_practice_info,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
