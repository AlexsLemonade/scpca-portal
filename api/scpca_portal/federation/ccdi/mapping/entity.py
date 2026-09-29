"""
What every CCDI entity has in common.

An entity is constructed from the ScPCA records behind it and knows two things:
what it is called, and how to find its peers in a set of records. Everything
else — which generated types it emits, which field map holds its getters — it
declares, so the wiring is readable in the entity's own module rather than
inferred from its name.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Iterable

from scpca_portal.federation.ccdi.mapping import NAMESPACE
from scpca_portal.federation.ccdi.mapping.field_map import FieldMap


class Entity(ABC):
    """One CCDI entity: the ScPCA records behind it, and how it emits."""

    # Declared by each entity. `ccdi_type` and `identifier` are the generated
    # types it emits; `FIELDS` holds the getters that populate its metadata.
    ccdi_type: ClassVar[type]
    identifier: ClassVar[type]
    FIELDS: ClassVar[FieldMap]

    @property
    @abstractmethod
    def name(self) -> str:
        """This entity's CCDI identifier."""

    @classmethod
    @abstractmethod
    def from_records(cls, records: Iterable) -> list["Entity"]:
        """
        The entities to emit, from ScPCA records an endpoint has already fetched.

        Abstract because every entity answers it differently — a Subject groups
        samples that share an identity, a Sample is one per library/sample pair —
        and because an endpoint needs the answer before it can page or count.
        """

    def emit(self, **fields: Any):
        """
        This entity as the type the spec defines.

        Every entity carries an id and metadata; `fields` is how a subclass adds
        the one that makes it what it is — a Subject's `kind`, a Sample's
        `subject`. Override `emit` to supply it, rather than calling this with
        fields from outside.

        Nothing sets `gateways`. The spec's link kinds describe how precisely a
        URL points at *the entity carrying it*, and the only URLs this node can
        build are per-CCDL-dataset — an exact fit for a File and a cohort link
        for a Sample or Subject. So gateways belong on File, and a consumer
        reaches a sample's downloads through the Files that name it.
        """
        return self.ccdi_type(
            id=self.identifier(namespace=NAMESPACE, name=self.name),
            metadata=self.FIELDS.build(self),
            **fields,
        )
