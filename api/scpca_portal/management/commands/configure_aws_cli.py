import logging
import subprocess

from django.core.management.base import BaseCommand

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


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

    def configure_aws_cli(self, **kwargs):
        commands = [
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#payload-signing-enabled
            "aws configure set default.s3.payload_signing_enabled false",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-concurrent-requests
            "aws configure set default.s3.max_concurrent_requests "
            f"{kwargs['s3_max_concurrent_requests']}",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#multipart-chunksize
            "aws configure set default.s3.multipart_chunksize "
            f"{kwargs['s3_multipart_chunk_size']}MB",
        ]
        if kwargs["s3_max_bandwidth"]:
            commands.append(
                # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-bandwidth
                f"aws configure set default.s3.max_bandwidth {kwargs['s3_max_bandwidth']}MB/s",
            )

        logger.info("Configuring AWS CLI...")
        for command in commands:
            subprocess.check_call(command.split())

        logger.info("AWS CLI successfully configured!")
