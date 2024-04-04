import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3
from botocore.client import Config

from django.conf import settings

from scpca_portal.models import ComputedFile, Sample
from scpca_portal import utils

from .file_downloader import Downloader
from .readme_generator import ReadMeGenerator
from .metadata_collector import MetadataCollector
from .file_archiver import FileArchiver
from .file_uploader import Uploader
from .cleanup import Cleanup

"""
The goal of this file is to handle downloaded files from S3 input bucket, to call relevant methods responsible for processing files and extracing metadata, and then to upload the processed files (as a zip archive) to an S3 output bucket.
"""

logger = logging.getLogger()
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class Loader():

    def load_data(self, sample_id=None, **kwargs) -> None:
        """
        Goes through a project directory contents, parses multiple level metadata
        files, writes combined metadata into resulting files.

        Returns a list of project's computed files.
        """

        Downloader.download_files(**kwargs)
        (
            combined_single_cell_metadata,
            combined_spatial_metadata,
            combined_multiplexed_metadata,
        ) = MetadataCollector.collect_metadata(**kwargs)
        ReadMeGenerator.create_readmes(kwargs.get("scpca_project_id"))
        FileArchiver.archive_file(
            combined_single_cell_metadata,
            combined_spatial_metadata,
            combined_multiplexed_metadata,
            **kwargs,
        )
        # Uploader.upload_files()
        Cleanup.clean_up_data(**kwargs)