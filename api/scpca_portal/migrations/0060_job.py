# Generated by Django 3.2.25 on 2025-02-12 23:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0059_auto_20250128_1510"),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("attempt", models.PositiveIntegerField(default=1)),
                ("critical_error", models.BooleanField(default=False)),
                ("failure_reason", models.TextField(blank=True, null=True)),
                ("retry_on_termination", models.BooleanField(default=False)),
                (
                    "state",
                    models.TextField(
                        choices=[
                            ("CREATED", "Created"),
                            ("SUBMITTED", "Submitted"),
                            ("COMPLETED", "Completed"),
                            ("COMPLETED", "Terminated"),
                        ],
                        default="CREATED",
                    ),
                ),
                ("submitted_at", models.DateTimeField(null=True)),
                ("completed_at", models.DateTimeField(null=True)),
                ("terminated_at", models.DateTimeField(null=True)),
                ("batch_job_name", models.TextField(null=True)),
                ("batch_job_definition", models.TextField(null=True)),
                ("batch_job_queue", models.TextField(null=True)),
                ("batch_container_overrides", models.JSONField(default=dict)),
                ("batch_job_id", models.TextField(null=True)),
                ("batch_status", models.TextField(null=True)),
                (
                    "dataset",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="jobs",
                        to="scpca_portal.dataset",
                    ),
                ),
            ],
            options={
                "db_table": "jobs",
                "ordering": ["updated_at"],
                "get_latest_by": "updated_at",
            },
        ),
    ]
