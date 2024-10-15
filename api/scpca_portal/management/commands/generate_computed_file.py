import logging
from typing import Dict

from django.core.management.base import BaseCommand

from scpca_portal import common, loader
from scpca_portal.models import Project, Sample

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


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
        parser.add_argument("--download-config", type=dict)

    def handle(self, *args, **kwargs):
        self.generate_computed_file(**kwargs)

    def generate_computed_file(
        self,
        project_id: str,
        sample_id: str,
        download_config: Dict,
        **kwargs,
    ) -> None:
        """Generates a project's computed files according predetermined download configurations"""
        loader.prep_data_dirs()

        if project_id:
            project = Project.objects.filter(scpca_id=project_id).first()
            sample = None
            if not project:
                logger.error("project doesn't exist")
                return
            if download_config not in common.GENERATED_PROJECT_DOWNLOAD_CONFIGS:
                logger.error("download_config is not valid")
                return
        elif sample_id:
            sample = Sample.objects.filter(scpca_id=sample_id).first()
            project = None
            if not sample:
                logger.error("sample doesn't exist")
                return
            if download_config not in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGS:
                logger.error("download_config is not valid")
                return

        else:
            logger.error(
                "neither project_id nor sample_id were passed. at least one must be passed."
            )
            return

        loader.generate_computed_file(
            download_config=download_config, project=project, sample=sample
        )
