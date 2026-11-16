from django.conf import settings
from django.db import migrations

# The shared input bucket every environment read from before the move to per-deploy buckets
OLD_INPUT_BUCKET = "scpca-portal-input"


def update_input_bucket(apps, from_bucket: str, to_bucket: str) -> None:
    # No-op where the setting still points at the old bucket (local, dev stacks).
    # In tests it runs, but against an empty test database.
    if from_bucket == to_bucket:
        return

    OriginalFile = apps.get_model("scpca_portal", "OriginalFile")
    Project = apps.get_model("scpca_portal", "Project")

    OriginalFile.objects.filter(s3_bucket=from_bucket).update(s3_bucket=to_bucket)
    Project.objects.filter(s3_input_bucket=from_bucket).update(s3_input_bucket=to_bucket)


def apply_input_bucket(apps, schema_editor):
    update_input_bucket(apps, OLD_INPUT_BUCKET, settings.AWS_S3_INPUT_BUCKET_NAME)


def reverse_input_bucket(apps, schema_editor):
    update_input_bucket(apps, settings.AWS_S3_INPUT_BUCKET_NAME, OLD_INPUT_BUCKET)


class Migration(migrations.Migration):

    dependencies = [
        ("scpca_portal", "0089_project_additional_processing_and_more"),
    ]

    operations = [
        migrations.RunPython(apply_input_bucket, reverse_code=reverse_input_bucket),
    ]
