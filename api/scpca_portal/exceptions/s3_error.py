class S3Error(Exception):
    def __init__(
        self, message: str | None = None, key: str = None, bucket_name: str = None
    ) -> None:
        default_message = "An error occurred during S3 operation."

        message = message or default_message
        super().__init__(message)


class S3TaggingError(S3Error):
    def __init__(self, key: str, bucket_name: str, tags: dict | None = None) -> None:
        message = f"Failed to tag {key} in {bucket_name} with {tags}."
        super().__init__(message, key, bucket_name, tags)


class S3UploadError(S3Error):
    def __init__(self, key: str, bucket_name: str) -> None:
        message = f"Failed to upload {key} to {bucket_name}."
        super().__init__(message, key, bucket_name)
