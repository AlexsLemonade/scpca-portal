# Generated by Django 3.2.25 on 2024-08-15 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0049_auto_20240806_1533"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="s3_input_bucket",
            field=models.TextField(default="scpca-portal-inputs"),
        ),
    ]
