# Generated by Django 3.2.25 on 2024-07-03 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0047_library_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="computedfile",
            name="includes_merged",
            field=models.BooleanField(default=False, null=True),
        ),
    ]