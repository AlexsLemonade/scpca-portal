# Generated by Django 3.2.25 on 2024-08-06 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0048_library_has_cite_seq_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sample",
            name="age_at_diagnosis",
        ),
        migrations.AddField(
            model_name="sample",
            name="age",
            field=models.TextField(default="NA"),
        ),
        migrations.AddField(
            model_name="sample",
            name="age_timing",
            field=models.TextField(default="NA"),
        ),
    ]
