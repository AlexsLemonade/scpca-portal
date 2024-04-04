
class Uploader():
    def upload_files():
        

    def process_computed_file(computed_file, clean_up_output_data, update_s3):
        """Processes saving, upload and cleanup of a single computed file."""
        logger.info(f"Processing {computed_file}")

        computed_file.save()
        if update_s3:
            logger.info(f"Uploading {computed_file}")
            computed_file.create_s3_file()
        if clean_up_output_data:
            computed_file.zip_file_path.unlink(missing_ok=True)

        # Close DB connection for each thread.
        connection.close()

    def create_s3_file(self):
        """Uploads the computed file to S3 using AWS CLI tool."""
        subprocess.check_call(
            (
                "aws",
                "s3",
                "cp",
                str(self.zip_file_path),
                f"s3://{settings.AWS_S3_BUCKET_NAME}/{self.s3_key}",
            )
        )

    def delete_s3_file(self, force=False):
        # If we're not running in the cloud then we shouldn't try to
        # delete something from S3 unless force is set.
        if not settings.UPDATE_S3_DATA and not force:
            return False

        try:
            s3.delete_object(Bucket=self.s3_bucket, Key=self.s3_key)
        except Exception:
            logger.exception(
                "Failed to delete S3 object for Computed File.",
                computed_file=self.id,
                s3_object=self.s3_key,
            )
            return False

        return True

    def create_download_url(self):
        """Creates a temporary URL from which the file can be downloaded."""
        if self.s3_bucket and self.s3_key:
            # Append the download date to the filename on download.
            date = utils.get_today_string()
            s3_key = Path(self.s3_key)

            return s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.s3_bucket,
                    "Key": self.s3_key,
                    "ResponseContentDisposition": (
                        f"attachment; filename = {s3_key.stem}_{date}{s3_key.suffix}"
                    ),
                },
                ExpiresIn=60 * 60 * 24 * 7,  # 7 days in seconds.
            )

