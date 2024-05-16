from typing import Dict

from django.db import models

from scpca_portal import common
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class Publication(TimestampedModel):
    """Publication class."""

    class Meta:
        db_table = "publications"

    doi = models.TextField(unique=True)
    citation = models.TextField()
    pi_name = models.TextField()

    def __str__(self) -> str:
        return self.doi

    @property
    def doi_url(self):
        """Returns DOI URL."""
        return f"https://doi.org/{self.doi}"

    @classmethod
    def get_from_dict(cls, data: Dict):
        publication = cls(
            doi=data.get("doi"),
            citation=data.get("citation"),
            pi_name=data.get("pi_name"),
        )

        return publication

    @staticmethod
    def bulk_create_from_project_data(project_data, project):
        """Creates a list of publication objects and saves them."""
        citations = [
            c.strip(common.STRIPPED_INPUT_VALUES)
            for c in project_data["citation"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        dois = [
            d.strip() for d in project_data["citation_doi"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        publications = []

        if len(citations) != len(dois):
            logger.error("Unable to add ambiguous publications.")
            return

        for idx, doi in enumerate(dois):
            if doi in common.IGNORED_INPUT_VALUES:
                continue

            # Skip if already in db
            if Publication.objects.filter(doi=doi):
                continue

            publication_data = {"doi": doi, "citation": citations[idx], "pi_name": project.pi_name}
            publications.append(Publication.get_from_dict(publication_data))

        Publication.objects.bulk_create(publications)
        project.publications.add(*publications)
