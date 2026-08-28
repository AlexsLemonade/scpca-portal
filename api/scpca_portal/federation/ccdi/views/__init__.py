"""
Read-only stub views for the CCDI federation node.

Every endpoint exists as a placeholder returning an empty body so the module's
routing and toggle can be exercised before the real responses land.

CCDI Federation API spec: https://cbiit.github.io/ccdi-federation-api/specification.html
"""

from scpca_portal.federation.ccdi.views.file import FileViewSet
from scpca_portal.federation.ccdi.views.info import InfoView
from scpca_portal.federation.ccdi.views.metadata_fields import MetadataFieldsView
from scpca_portal.federation.ccdi.views.namespace import NamespaceViewSet
from scpca_portal.federation.ccdi.views.organization import OrganizationViewSet
from scpca_portal.federation.ccdi.views.sample import SampleViewSet
from scpca_portal.federation.ccdi.views.schema import SchemaView
from scpca_portal.federation.ccdi.views.subject import SubjectViewSet
