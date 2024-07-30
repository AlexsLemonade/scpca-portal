# Generated by Django 3.2.25 on 2024-06-11 16:37

import django.db.models.deletion
from django.db import migrations, models


def apply_project(apps, schema_editor):
    Library = apps.get_model("scpca_portal", "library")

    for library in Library.objects.all():
        library.project = library.samples.first().project
        library.save()


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0046_project_data_file_paths"),
    ]

    operations = [
        migrations.AddField(
            model_name="library",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="libraries",
                to="scpca_portal.Project",
            ),
        ),
        migrations.RunPython(apply_project),
    ]
