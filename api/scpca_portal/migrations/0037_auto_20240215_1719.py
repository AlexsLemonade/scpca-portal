# Generated by Django 3.2.23 on 2024-02-15 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0036_computedfile_includes_merged"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="includes_merged_anndata",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="includes_merged_sce",
            field=models.BooleanField(default=False),
        ),
    ]