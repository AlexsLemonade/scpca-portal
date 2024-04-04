import subprocess


class Downloader():
    def download_files(self, *args, **kwargs):
        self.configure_aws_cli(**kwargs)
        project = self.load_data(**kwargs)
        return project

    @staticmethod
    def configure_aws_cli(**params):
        commands = [
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#payload-signing-enabled
            "aws configure set default.s3.payload_signing_enabled false",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-concurrent-requests
            "aws configure set default.s3.max_concurrent_requests "
            f"{params['s3_max_concurrent_requests']}",
            # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#multipart-chunksize
            "aws configure set default.s3.multipart_chunksize "
            f"{params['s3_multipart_chunk_size']}MB",
        ]
        if params["s3_max_bandwidth"] is not None:
            commands.append(
                # https://docs.aws.amazon.com/cli/latest/topic/s3-config.html#max-bandwidth
                f"aws configure set default.s3.max_bandwidth {params['s3_max_bandwidth']}MB/s",
            )

        for command in commands:
            subprocess.check_call(command.split())

    @staticmethod
    def download_data(bucket_name, scpca_project_id=None, scpca_sample_id=None):
        command_list = ["aws", "s3", "sync", f"s3://{bucket_name}", common.INPUT_DATA_PATH]
        if scpca_sample_id:
            command_list.extend(
                (
                    "--exclude=*",  # Must precede include patterns.
                    "--include=project_metadata.csv",
                    f"--include={scpca_project_id}/{scpca_sample_id}*",
                )
            )
        elif scpca_project_id:
            command_list.extend(
                (
                    "--exclude=*",  # Must precede include patterns.
                    "--include=project_metadata.csv",
                    f"--include={scpca_project_id}*",
                )
            )
        else:
            command_list.append("--delete")

        if "public-test" in bucket_name:
            command_list.append("--no-sign-request")

        subprocess.check_call(command_list)

    def load_data(
        self,
        allowed_submitters: set[str] = None,
        input_bucket_name: str = "scpca-portal-inputs",
        **kwargs,
    ):
        """Loads data from S3. Creates projects and loads data for them."""

        # Prepare data input directory.
        common.INPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        # Prepare data output directory.
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)
        common.OUTPUT_DATA_PATH.mkdir(exist_ok=True, parents=True)

        allowed_submitters = allowed_submitters or ALLOWED_SUBMITTERS
        project_id = kwargs.get("scpca_project_id")
        sample_id = kwargs.get("scpca_sample_id")

        if not kwargs.get("skip_sync"):
            self.download_data(
                input_bucket_name, scpca_project_id=project_id, scpca_sample_id=sample_id
            )
