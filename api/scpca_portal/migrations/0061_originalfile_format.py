# Generated by Django 3.2.25 on 2025-02-14 18:33

from django.db import migrations, models

from scpca_portal.enums.file_formats import FileFormats


def apply_format(apps, schema_editor):
    OriginalFile = apps.get_model("scpca_portal", "original_file")

    for original_file in OriginalFile.objects.all():
        if original_file.is_single_cell_experiment:
            original_file.format = FileFormats.SINGLE_CELL_EXPERIMENT
        elif original_file.is_anndata:
            original_file.format = FileFormats.ANN_DATA
        elif original_file.is_supplementary:
            original_file.format = FileFormats.SUPPLEMENTARY
        elif original_file.is_metadata:
            original_file.format = FileFormats.METADATA
        else:
            original_file.format = None

        original_file.save()


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0060_auto_20250214_1744"),
    ]

    operations = [
        migrations.AddField(
            model_name="originalfile",
            name="format",
            field=models.TextField(
                choices=[
                    ("ANN_DATA", "AnnData"),
                    ("SINGLE_CELL_EXPERIMENT", "Single cell experiment"),
                    ("METADATA", "Metadata"),
                    ("SUPPLEMENTARY", "Supplementary"),
                ],
                default=None,
                null=True,
            ),
        ),
    ]
