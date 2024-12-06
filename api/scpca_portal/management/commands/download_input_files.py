import logging

from django.core.management.base import BaseCommand

from scpca_portal import common, loader, s3
from scpca_portal.models import Project

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        loader.prep_data_dirs()

        project = Project.objects.filter(scpca_id="SCPCP000006").first()

        download_config = common.PROJECT_DOWNLOAD_CONFIGS["SPATIAL_SINGLE_CELL_EXPERIMENT"]
        libraries = project.get_libraries(download_config)

        library_data_file_paths = [
            fp for lib in libraries for fp in lib.get_download_config_file_paths(download_config)
        ]
        project_data_file_paths = project.get_download_config_file_paths(download_config)

        s3.download_input_files(
            library_data_file_paths + project_data_file_paths, project.s3_input_bucket
        )
