# Generated by Django 3.2.25 on 2025-01-27 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0057_auto_20250124_1413"),
    ]

    operations = [
        migrations.AddField(
            model_name="originalfile",
            name="is_cite_seq",
            field=models.BooleanField(default=False),
        ),
    ]
