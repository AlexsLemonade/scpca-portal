# Generated by Django 3.2.22 on 2023-11-08 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0031_alter_computedfile_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="includes_anndata",
            field=models.BooleanField(default=False),
        ),
    ]
