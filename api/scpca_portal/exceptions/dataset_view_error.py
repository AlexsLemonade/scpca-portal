from rest_framework import status
from rest_framework.exceptions import APIException


class DatasetViewError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid request: A dataset view error occurred."
    default_code = "bad_request"

    def __init__(self, detail: str | None = None, code: str | None = None):
        detail = detail or self.default_detail
        code = code or self.default_code
        super().__init__(detail, code)


class DatasetFormatChangeError(DatasetViewError):
    default_detail = "Invalid request: Dataset with data cannot change format."


class UpdateProcessingDatasetError(DatasetViewError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Invalid request: Processing datasets cannot be modified."
    default_code = "conflict"
