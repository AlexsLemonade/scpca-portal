# Generated by Django 3.2.25 on 2024-03-20 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0037_merge_20240220_1750"),
    ]

    operations = [
        migrations.AddField(
            model_name="sample",
            name="is_cell_line",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sample",
            name="is_xenograft",
            field=models.BooleanField(default=False),
        ),
    ]
