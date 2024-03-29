# Generated by Django 3.2.16 on 2022-12-14 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0026_auto_20220720_1738"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.TextField()),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("pi_name", models.TextField()),
            ],
            options={
                "db_table": "contacts",
            },
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("doi", models.TextField(unique=True)),
                ("citation", models.TextField()),
                ("pi_name", models.TextField()),
            ],
            options={
                "db_table": "publications",
            },
        ),
    ]
