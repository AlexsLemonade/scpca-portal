# Generated by Django 2.2.24 on 2022-04-14 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0011_auto_20220414_1857"),
    ]

    operations = [
        migrations.AlterField(
            model_name="computedfile",
            name="type",
            field=models.TextField(
                choices=[
                    ("PROJECT_SPATIAL_ZIP", "Project Spatial ZIP"),
                    ("PROJECT_ZIP", "Project ZIP"),
                    ("SAMPLE_SPATIAL_ZIP", "Sample Spatial ZIP"),
                    ("SAMPLE_ZIP", "Sample ZIP"),
                ]
            ),
        ),
    ]
