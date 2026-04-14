"""The serializers included in this directory can be used for nested relationships.

These serializers do not use nested relationships themselves, so that
if a sample object links to a computed file and the computed file
links to the sample, the JSON won't recur infinitely. For any
relationships, these serializers will use PrimaryKeyRelatedFields or
SlugRelatedFields.

The one exception is the ProjectSerializer because it will always include its summaries.
"""

from scpca_portal.serializers.ccdl_dataset import CCDLDatasetDetailSerializer, CCDLDatasetSerializer
from scpca_portal.serializers.computed_file import ComputedFileSerializer
from scpca_portal.serializers.contact import ContactSerializer
from scpca_portal.serializers.external_accession import ExternalAccessionSerializer
from scpca_portal.serializers.project import (
    ProjectDetailSerializer,
    ProjectLeafSerializer,
    ProjectSerializer,
)
from scpca_portal.serializers.project_summary import ProjectSummarySerializer
from scpca_portal.serializers.publication import PublicationSerializer
from scpca_portal.serializers.sample import SampleSerializer
from scpca_portal.serializers.user_dataset import (
    UserDatasetCreateSerializer,
    UserDatasetDetailSerializer,
    UserDatasetSerializer,
    UserDatasetUpdateSerializer,
)
