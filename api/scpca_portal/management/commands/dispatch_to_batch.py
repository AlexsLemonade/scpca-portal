import logging
import os

from django.core.management.base import BaseCommand

import boto3

from scpca_portal import common
from scpca_portal.models import Project

batch = boto3.client("batch", region_name=os.environ["AWS_REGION"])
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    help = """
    Submits all computed file combinations to the specified AWS Batch job queue
    for projects for which computed files have yet to be generated for them.
    If a project-id is passed, then computed files are only submitted for that specific project.
    """

    def add_arguments(self, parser):
        parser.add_argument("--project-id", type=str)

    def handle(self, *args, **kwargs):
        self.dispatch_to_batch(**kwargs)

    def submit_job(
        self, *, download_config_name: str, project_id: str = "", sample_id: str = ""
    ) -> None:
        """
        Submit job to AWS Batch, accordingly to the resource_id and download_config combination.
        """
        resource_flag = "--project_id" if project_id else "--sample_id"
        resource_id = project_id if project_id else sample_id
        job_name = f"{resource_id} - {download_config_name}"

        response = batch.submit_job(
            jobName=job_name,
            jobQueue="scpca_portal_project",
            jobDefinition="scpca_portal_project",
            containerOverrides={
                "command": [
                    "python",
                    "manage.py",
                    "generate_computed_file",
                    resource_flag,
                    resource_id,
                    "--download-config-name",
                    download_config_name,
                ],
            },
        )

        logger.info(f'{job_name} submitted to Batch with jobId {response["jobId"]}')

    def dispatch_to_batch(self, project_id: str = ""):
        """
        Iterate over all projects that don't have computed files and submit each
        resource_id and download_config combination to the Batch queue.
        If a project id is passed, then computed files are created for all combinations
        within that project.
        """
        projects = (
            Project.objects.filter(project_computed_files__is_null=True)
            if not project_id
            else Project.objects.filter(scpca_id=project_id)
        )

        for project in projects:
            for download_config_name in common.PROJECT_DOWNLOAD_CONFIGS.keys():
                self.submit_job(
                    project_id=project.scpca_id, download_config_name=download_config_name
                )

            for sample in project.samples_to_generate:
                for download_config_name in common.SAMPLE_DOWNLOAD_CONFIGS.keys():
                    self.submit_job(
                        sample_id=sample.scpca_id, download_config_name=download_config_name
                    )
