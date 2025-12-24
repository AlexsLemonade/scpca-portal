import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
from botocore.client import Config

from scpca_portal.config.logging import get_and_configure_logger

logger = get_and_configure_logger(__name__)

boto3.client("s3", config=Config(signature_version="s3v4", region_name=settings.AWS_REGION))


class Command(BaseCommand):
    help = """Configures the AWS CLI.

    Current supported options include:
        --s3-max-bandwidth
        --s3-max-concurrent-requests
        --s3-multipart-chunk-size

    The configuration works by writing the config values to ~/.aws/config,
    which is references by the AWS CLI tool each time its called."""

    def add_arguments(self, parser):
        parser.add_argument("--s3-max-bandwidth", type=int, default=None, help="In MB/s")
        parser.add_argument("--s3-max-concurrent-requests", type=int, default=10)
        parser.add_argument("--s3-multipart-chunk-size", type=int, default=8, help="In MB")

    def handle(self, *args, **kwargs):
        self.configure_aws_cli(**kwargs)

    def configure_aws_cli(
        self,
        *,
        s3_max_concurrent_requests: int = 10,
        s3_multipart_chunk_size: int = 8,
        s3_max_bandwidth: int,
        **kwargs,
    ):
        commands = [
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#payload-signing-enabled
            "aws configure set default.s3.payload_signing_enabled false",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-concurrent-requests
            f"aws configure set default.s3.max_concurrent_requests {s3_max_concurrent_requests}",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#multipart-chunksize
            f"aws configure set default.s3.multipart_chunksize {s3_multipart_chunk_size}MB",
        ]

        if s3_max_bandwidth:
            commands.append(
                # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-bandwidth
                f"aws configure set default.s3.max_bandwidth {s3_max_bandwidth}MB/s",
            )

        logger.info("Configuring AWS CLI...")
        for command in commands:
            subprocess.check_call(command.split())

        logger.info("AWS CLI successfully configured!")
