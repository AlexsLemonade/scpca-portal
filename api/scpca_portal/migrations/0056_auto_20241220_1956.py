# Generated by Django 3.2.25 on 2024-12-20 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0055_originalfile"),
    ]

    operations = [
        migrations.AddField(
            model_name="originalfile",
            name="is_metadata",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="originalfile",
            name="last_bucket_sync",
            field=models.DateTimeField(),
            preserve_default=False,
        ),
    ]