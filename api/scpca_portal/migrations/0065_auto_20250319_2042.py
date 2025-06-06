# Generated by Django 3.2.25 on 2025-03-19 20:42

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0064_auto_20250313_1651"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dataset",
            name="is_metadata_only",
        ),
        migrations.AddField(
            model_name="dataset",
            name="ccdl_name",
            field=models.TextField(
                choices=[
                    ("SINGLE_CELL_SINGLE_CELL_EXPERIMENT", "Single Cell Single Cell Experiment"),
                    (
                        "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED",
                        "Single Cell Single Cell Experiment No Multiplexed",
                    ),
                    (
                        "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED",
                        "Single Cell Single Cell Experiment Merged",
                    ),
                    ("SINGLE_CELL_ANN_DATA", "Single Cell Ann Data"),
                    ("SINGLE_CELL_ANN_DATA_MERGED", "Single Cell Ann Data Merged"),
                    ("SPATIAL_SINGLE_CELL_EXPERIMENT", "Spatial Single Cell Experiment"),
                    ("ALL_METADATA", "All Metadata"),
                    (
                        "SAMPLE_SINGLE_CELL_SINGLE_CELL_EXPERIMENT",
                        "Sample Single Cell Single Cell Experiment",
                    ),
                    ("SAMPLE_SINGLE_CELL_ANN_DATA", "Sample Single Cell Ann Data"),
                    (
                        "SAMPLE_SPATIAL_SINGLE_CELL_EXPERIMENT",
                        "Sample Spatial Single Cell Experiment",
                    ),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="dataset",
            name="ccdl_project_id",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="dataset",
            name="format",
            field=models.TextField(
                choices=[
                    ("ANN_DATA", "Ann Data"),
                    ("SINGLE_CELL_EXPERIMENT", "Single Cell Experiment"),
                    ("METADATA", "Metadata"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="state",
            field=models.TextField(
                choices=[
                    ("CREATED", "Created"),
                    ("SUBMITTED", "Submitted"),
                    ("COMPLETED", "Completed"),
                    ("TERMINATED", "Terminated"),
                ],
                default="CREATED",
            ),
        ),
        migrations.AlterField(
            model_name="library",
            name="formats",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(
                    choices=[
                        ("ANN_DATA", "Ann Data"),
                        ("SINGLE_CELL_EXPERIMENT", "Single Cell Experiment"),
                        ("METADATA", "Metadata"),
                        ("SUPPLEMENTARY", "Supplementary"),
                    ]
                ),
                default=list,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="library",
            name="modality",
            field=models.TextField(
                choices=[
                    ("BULK_RNA_SEQ", "Bulk RNA-seq"),
                    ("CITE_SEQ", "CITE-seq"),
                    ("MULTIPLEXED", "Multiplexed"),
                    ("SINGLE_CELL", "Single Cell"),
                    ("SPATIAL", "Spatial Data"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="originalfile",
            name="formats",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(
                    choices=[
                        ("ANN_DATA", "Ann Data"),
                        ("SINGLE_CELL_EXPERIMENT", "Single Cell Experiment"),
                        ("METADATA", "Metadata"),
                        ("SUPPLEMENTARY", "Supplementary"),
                    ]
                ),
                default=list,
                size=None,
            ),
        ),
    ]
