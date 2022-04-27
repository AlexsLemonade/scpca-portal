import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.models import Project

logger = logging.getLogger()


class Command(BaseCommand):
    help = """Deletes all data related to a project with ScPCA ID `scpca_id`."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-from-s3",
            default=settings.UPDATE_S3_DATA,
            type=bool,
            help=(
                "True or False, will force or prevent deletion of S3 data. Defaults to "
                "True in the cloud and False locally."
            ),
        )
        parser.add_argument(
            "--scpca-id", help="The ScPCA ID for project whose data will be deleted."
        )

    def handle(self, *args, **options):
        for project in Project.objects.filter(scpca_id=options["scpca_id"]):
            logger.info(f"Purging '{project}'")
            project.purge(delete_from_s3=options["delete_from_s3"])
