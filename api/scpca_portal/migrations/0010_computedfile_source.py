# Generated by Django 2.2.24 on 2022-04-14 18:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0009_project_downloadable_sample_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="computedfile",
            name="prjct",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_computed_file",
                to="scpca_portal.Project",
            ),
        ),
    ]
