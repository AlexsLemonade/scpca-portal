# Generated by Django 2.2.24 on 2021-09-10 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="has_cite_seq_data",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="has_spatial_data",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="modalities",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sample",
            name="has_spatial_data",
            field=models.BooleanField(default=False),
        ),
    ]
