# Generated by Django 3.2.13 on 2022-06-02 17:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0017_auto_20220512_1757"),
    ]

    operations = [
        migrations.AddField(
            model_name="sample",
            name="multiplexed_with",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), default=list, size=None
            ),
        ),
    ]
