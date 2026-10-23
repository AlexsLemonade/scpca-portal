"""
Pydantic response types for the CCDI node, generated from the vendored spec.

The generated models live in `_models.py` (regenerate with
`./manage.py generate_ccdi_types`). Re-export the ones the views use under clean
names here as endpoints are implemented.

Only types the spec names are aliased here. The spec also expresses some types as
anonymous `oneOf` variants — gateways, links, error kinds — and the generator
numbers those positionally, so they have no stable name to import. Nothing needs
them yet; whatever does will have to resolve them by discriminator rather than by
number.

`dump` is how every view turns one of these into a response body.
"""

from typing import Any

from scpca_portal.federation.ccdi.schema._models import (
    ModelsFile as File,
    ModelsFileIdentifier as FileIdentifier,
    ModelsFileMetadata as FileMetadata,
    ModelsMetadataFieldDescriptionHarmonized as HarmonizedFieldDescription,
    ModelsMetadataFieldDescriptionHarmonizedStandard as FieldStandard,
    ModelsMetadataFieldDescriptionUnharmonized as UnharmonizedFieldDescription,
    ModelsNamespaceIdentifier as NamespaceIdentifier,
    ModelsSample as Sample,
    ModelsSampleIdentifier as SampleIdentifier,
    ModelsSampleMetadata as SampleMetadata,
    ModelsSubject as Subject,
    ModelsSubjectIdentifier as SubjectIdentifier,
    ModelsSubjectMetadata as SubjectMetadata,
    ResponsesEntityCounts as EntityCounts,
    ResponsesEntitySummary as EntitySummary,
    ResponsesInformation as InfoResponse,
    ResponsesMetadataFieldDescriptions as MetadataFieldsResponse,
    ResponsesNamespace as NamespaceResponse,
    ResponsesNamespaces as NamespacesResponse,
    ResponsesOrganization as OrganizationResponse,
    ResponsesOrganizations as OrganizationsResponse,
    ResponsesSamples as SamplesResponse,
)


def dump(built: Any) -> dict:
    """
    Render a built spec type as a response body.

    The spec has optional fields it never marks nullable — `metadata.unharmonized`
    is one — while the generated types default them to `None`. `exclude_unset`
    drops those; without it they emit as `null`, which the contract rejects.

    Set a field explicitly, even to `None`, to emit a null.
    """
    return built.model_dump(mode="json", by_alias=True, exclude_unset=True)
