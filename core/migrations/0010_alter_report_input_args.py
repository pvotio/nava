# Generated by Django 4.2.15 on 2025-02-27 14:27

import core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_delete_filemanagerpermissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='input_args',
            field=core.fields.AzureSafeJSONField(default=dict),
        ),
    ]
