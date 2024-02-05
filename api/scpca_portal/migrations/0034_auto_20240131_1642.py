# Generated by Django 3.2.22 on 2024-01-31 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0033_computedfile_modality"),
    ]

    operations = [
        migrations.AddField(
            model_name="computedfile",
            name="has_bulk_rna_seq",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="computedfile",
            name="has_cite_seq_data",
            field=models.BooleanField(default=False),
        ),
    ]