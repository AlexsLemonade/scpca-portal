# Generated by Django 3.2.18 on 2024-04-12 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0039_computedfile_includes_celltype_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="computedfile",
            name="includes_merged",
            field=models.BooleanField(default=False),
        ),
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
