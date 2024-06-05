from typing import Dict

from django.db import models

from scpca_portal import common, utils
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

    @classmethod
    def bulk_create_from_project_data(cls, project_data, project):
        """Creates a list of publication objects and saves them."""
        publications = []

        try:
            zipped_publication_details = utils.get_csv_zipped_values(
                project_data, "doi", "citation"
            )
        except Exception:
            logger.error("Unable to add ambiguous publications.")
            raise

        for doi, citation in zipped_publication_details:
            if doi in common.IGNORED_INPUT_VALUES:
                continue

            publication_data = {
                "doi": doi.strip(),
                "citation": citation.strip(common.STRIPPED_INPUT_VALUES),
                "pi_name": project.pi_name,
            }

            # Handle case where contact is already in db
            if existing_publication := Publication.objects.filter(
                doi=publication_data["doi"]
            ).first():
                if existing_publication not in project.publications.all():
                    project.publications.add(existing_publication)
                continue

            publications.append(Publication.get_from_dict(publication_data))

        Publication.objects.bulk_create(publications)
        project.publications.add(*publications)
