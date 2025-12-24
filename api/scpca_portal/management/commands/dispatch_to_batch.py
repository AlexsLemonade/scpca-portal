from argparse import BooleanOptionalAction
from collections import Counter

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models import Job, Project

logger = get_and_configure_logger(__name__)


class Command(BaseCommand):
    help = """
    Submits all computed file combinations to the specified AWS Batch job queue
    for projects for which computed files have yet to be generated for them.
    If regenerate-all is passed, then presence of existing computed files are ignored.
    If a project-id is passed, then all other projects will be ignored.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--regenerate-all", action=BooleanOptionalAction, type=bool, default=False
        )
        parser.add_argument("--project-id", type=str, default="")
        # for now, we're only notifying on submission of the last project job
        parser.add_argument("--notify", type=bool, default=False, action=BooleanOptionalAction)

    def handle(self, *args, **kwargs):
        self.dispatch_to_batch(**kwargs)

    def dispatch_to_batch(self, project_id: str, regenerate_all: bool, notify: bool, **kwargs):
        """
        Iterate over all projects that fit the criteria of the passed flags
        and submit jobs to Batch accordingly.
        """
        projects = Project.objects.all()

        if not regenerate_all:
            projects = projects.filter(project_computed_files__isnull=True)

        if project_id:
            projects = projects.filter(scpca_id=project_id)

        job_counts = Counter()

        project_list = list(projects)  # convert to list to be able to index below
        for project in project_list:
            project_valid_download_config_names = project.valid_download_config_names
            for download_config_name in project_valid_download_config_names:
                is_last_job = (
                    project == project_list[-1]
                    and download_config_name == project_valid_download_config_names[-1]
                )
                job = Job.get_project_job(
                    project_id=project.scpca_id,
                    download_config_name=download_config_name,
                    notify=is_last_job and notify,
                )

                job.submit()
                job_counts["project"] += 1

            for sample in project.samples_to_generate:
                for download_config_name in sample.valid_download_config_names:
                    job = Job.get_sample_job(
                        sample_id=sample.scpca_id,
                        download_config_name=download_config_name,
                    )

                    job.submit()
                    job_counts["sample"] += 1

        total_job_count = sum(job_counts.values())
        logger.info(
            "Job submission complete. "
            f"{total_job_count} job{pluralize(total_job_count)} were submitted "
            f"({job_counts['project']} project job{pluralize(job_counts['project'])}, "
            f"{job_counts['sample']} sample job{pluralize(job_counts['sample'])})."
        )
