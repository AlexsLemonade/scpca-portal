# Generated by Django 3.2.22 on 2023-10-30 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0029_auto_20221217_0256"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalAccession",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("accession", models.TextField(primary_key=True, serialize=False)),
                ("has_raw", models.BooleanField(default=False)),
                ("url", models.TextField()),
            ],
            options={
                "db_table": "external_accessions",
            },
        ),
        migrations.AddField(
            model_name="project",
            name="external_accessions",
            field=models.ManyToManyField(to="scpca_portal.ExternalAccession"),
        ),
    ]