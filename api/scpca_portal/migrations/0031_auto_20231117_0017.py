# Generated by Django 3.2.22 on 2023-11-17 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0030_auto_20231030_2259"),
    ]

    operations = [
        migrations.AddField(
            model_name="computedfile",
            name="format",
            field=models.TextField(
                choices=[
                    ("ANN_DATA", "AnnData"),
                    ("SINGLE_CELL_EXPERIMENT", "Single cell experiment"),
                ],
                default="SINGLE_CELL_EXPERIMENT",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="project",
            name="includes_anndata",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sample",
            name="includes_anndata",
            field=models.BooleanField(default=False),
        ),
    ]