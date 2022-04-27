from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.models import Project, ProjectSummary


def purge_project(scpca_id: str, delete_from_s3=False) -> None:
    """Deletes all projects with pi_name and their associated data."""
    projects = Project.objects.filter(scpca_id=scpca_id)

    if projects.count() == 0:
        print(f"Project with ScPCA ID {scpca_id} does not exist.")
        return

    for project in projects:
        for sample in project.samples.all():

            if sample.computed_file:
                if delete_from_s3:
                    sample.computed_file.delete_s3_file(force=True)

                sample.computed_file.delete()

            sample.delete()

        if project.computed_file:
            if delete_from_s3:
                project.computed_file.delete_s3_file(force=True)

            project.computed_file.delete()

        ProjectSummary.objects.filter(project=project).delete()

        project.delete()

        print(f"Purged project with ScPCA ID {scpca_id}")


class Command(BaseCommand):
    help = """Deletes all projects with scpca_id and their associated data."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--scpca-id", help="The ScPCA ID for project whose data will be deleted."
        )
        parser.add_argument(
            "--delete-from-s3",
            default=settings.UPDATE_IMPORTED_DATA,
            type=bool,
            help=(
                "True or False, will force or prevent deletion of S3 data. Defaults to "
                "True in the cloud and False locally."
            ),
        )

    def handle(self, *args, **options):
        purge_project(options["scpca_id"], options["delete_from_s3"])
