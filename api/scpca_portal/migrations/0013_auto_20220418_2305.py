# Generated by Django 2.2.24 on 2022-04-18 23:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0012_auto_20220414_2320"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sample",
            name="computed_file",
        ),
        migrations.AddField(
            model_name="computedfile",
            name="smpl",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sample_computed_files",
                to="scpca_portal.Sample",
            ),
        ),
    ]
