# Generated by Django 3.2.25 on 2024-10-10 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0052_auto_20240929_1357"),
    ]

    operations = [
        migrations.RenameField(
            model_name="sample",
            old_name="demux_cell_count_estimate",
            new_name="demux_cell_count_estimate_sum",
        ),
    ]
