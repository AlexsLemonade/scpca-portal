from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.models import Project, ProjectSummary


def purge_project(pi_name: str, delete_from_s3=False) -> None:
    """Deletes all projects with pi_name and their associated data.
    """
    projects = Project.objects.filter(pi_name=pi_name)

    if projects.count() == 0:
        print(f"Project with PI named {pi_name} does not exist.")
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

        print(f"Purged project with PI named {pi_name}")


class Command(BaseCommand):
    help = """Deletes all projects with pi_name and their associated data."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--pi-name", help="The name of a PI whose project's data will be deleted."
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
        purge_project(options["pi_name"], options["delete_from_s3"])
