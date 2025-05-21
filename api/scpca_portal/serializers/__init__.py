"""The serializers included in this directory can be used for nested relationships.

These serializers do not use nested relationships themselves, so that
if a sample object links to a computed file and the computed file
links to the sample, the JSON won't recur infinitely. For any
relationships, these serializers will use PrimaryKeyRelatedFields or
SlugRelatedFields.

The one exception is the ProjectSerializer because it will always include its summaries.
"""

from .computed_file import ComputedFileSerializer
from .contact import ContactSerializer
from .dataset import (
    DatasetCreateSerializer,
    DatasetDetailSerializer,
    DatasetSerializer,
    DatasetUpdateSerializer,
)
from .external_accession import ExternalAccessionSerializer
from .project import ProjectLeafSerializer, ProjectSerializer
from .project_summary import ProjectSummarySerializer
from .publication import PublicationSerializer
from .sample import SampleSerializer
