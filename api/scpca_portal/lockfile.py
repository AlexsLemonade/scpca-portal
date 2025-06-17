from django.conf import settings

from scpca_portal import common, s3


def get_is_lockfile_empty():
    return s3.check_file_empty(common.LOCKFILE_KEY, settings.AWS_S3_INPUT_BUCKET_NAME)
