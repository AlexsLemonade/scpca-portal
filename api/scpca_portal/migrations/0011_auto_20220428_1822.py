# Generated by Django 2.2.24 on 2022-04-28 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0010_auto_20220428_1812"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="apitoken",
            table="api_tokens",
        ),
    ]
