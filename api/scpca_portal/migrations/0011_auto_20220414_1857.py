# Generated by Django 2.2.24 on 2022-04-14 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0010_computedfile_source"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="computed_file",),
    ]
