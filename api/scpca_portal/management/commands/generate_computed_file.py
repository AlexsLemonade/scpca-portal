from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand

from scpca_portal import common, loader, notifications, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Project, Sample

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    This command is meant to be called as an entrypoint to AWS Batch Fargate job instance.
    Individual files are computed according:
        - To the project or sample id
        - An appropriate corresponding download config

    When computation is completed, files are uploaded to S3, and the job is marked as completed.

    At which point the instance which generated this computed file will receive a new job
    from the job queue and begin computing the next file.
    """

    def add_arguments(self, parser):
        parser.add_argument("--project-id", type=str)
        parser.add_argument("--sample-id", type=str)
        parser.add_argument("--download-config-name", type=str)
        parser.add_argument("--notify", default=False, action=BooleanOptionalAction)

    def handle(self, *args, **kwargs):
        self.generate_computed_file(**kwargs)

    def generate_computed_file(
        self,
        project_id: str,
        sample_id: str,
        download_config_name: str,
        notify: bool,
        **kwargs,
    ) -> None:
        """Generates a project's computed files according predetermined download configurations"""
        utils.create_data_dirs()

        ids_not_mutually_exclusive = project_id and sample_id or (not project_id and not sample_id)
        if ids_not_mutually_exclusive:
            logger.error(
                "Invalid id combination. Passed ids must be mutually exclusive."
                "Either a project_id or a sample_id must be passed, but not both or neither."
            )

        if project_id:
            project = Project.objects.filter(scpca_id=project_id).first()
            if not project:
                logger.error(f"{project} does not exist.")
            if download_config_name not in common.PROJECT_DOWNLOAD_CONFIGS.keys():
                logger.error(f"{download_config_name} is not a valid project download config name.")
                logger.info(
                    f"Here are valid download_config_name values for projects: "
                    f"{common.PROJECT_DOWNLOAD_CONFIGS.keys()}"
                )
            download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
            loader.generate_computed_file(project=project, download_config=download_config)

        if sample_id:
            sample = Sample.objects.filter(scpca_id=sample_id).first()
            if not sample:
                logger.error(f"{sample} does not exist.")
            if download_config_name not in common.SAMPLE_DOWNLOAD_CONFIGS.keys():
                logger.error(f"{download_config_name} is not a valid sample download config name.")
                logger.info(
                    f"Here are valid download_config_name values for samples: "
                    f"{common.SAMPLE_DOWNLOAD_CONFIGS.keys()}"
                )
            download_config = common.SAMPLE_DOWNLOAD_CONFIGS[download_config_name]
            loader.generate_computed_file(sample=sample, download_config=download_config)

        if notify and project_id:
            notifications.send_project_files_completed_email(project_id)
