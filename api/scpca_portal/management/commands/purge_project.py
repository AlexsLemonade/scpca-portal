from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.project import Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """Deletes all data related to a project with ScPCA ID `scpca_id`."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-from-s3",
            action="store_true",
            default=settings.UPDATE_S3_DATA,
            help=(
                "True or False, will force or prevent deletion of S3 data. Defaults to "
                "True in the cloud and False locally."
            ),
        )
        parser.add_argument(
            "--scpca-id",
            help="The ScPCA ID for project whose data will be deleted.",
            required=True,
            type=str,
        )

    def handle(self, *args, **options):
        try:
            project = Project.objects.get(scpca_id=options["scpca_id"])
            logger.info(f"Purging '{project}'")
            project.purge(delete_from_s3=options["delete_from_s3"])
        except Project.DoesNotExist:
            logger.error(f"Project with scpca_id {options['scpca_id']} not found")
