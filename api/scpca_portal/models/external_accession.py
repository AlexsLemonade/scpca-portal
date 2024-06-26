from typing import Dict

from django.db import models

from scpca_portal import common, utils
from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.models.base import TimestampedModel

logger = get_and_configure_logger(__name__)


class ExternalAccession(TimestampedModel):
    """External accession."""

    class Meta:
        db_table = "external_accessions"

    accession = models.TextField(primary_key=True)
    has_raw = models.BooleanField(default=False)
    url = models.TextField()

    def __str__(self) -> str:
        return self.accession

    @classmethod
    def get_from_dict(cls, data: Dict):
        external_accession = cls(
            accession=data.get("accession"),
            has_raw=data.get("has_raw"),
            url=data.get("url"),
        )

        return external_accession

    @classmethod
    def bulk_create_from_project_data(cls, project_data, project):
        """Creates a list of external accession objects and saves them."""
        external_accessions = []

        try:
            zipped_external_accession_details = utils.get_csv_zipped_values(
                project_data, "accession", "has_raw", "accession_url"
            )
        except Exception:
            logger.error("Unable to add ambiguous external accessions.")
            raise

        for accession, has_raw, url in zipped_external_accession_details:
            if accession in common.IGNORED_INPUT_VALUES:
                continue

            external_accession_data = {
                "accession": accession.strip(),
                "has_raw": utils.boolean_from_string(has_raw.strip()),
                "url": url.strip(common.STRIPPED_INPUT_VALUES),
            }

            # Handle case where external accession is already in db
            if existing_accession := ExternalAccession.objects.filter(
                accession=external_accession_data["accession"]
            ).first():
                if existing_accession not in project.external_accessions.all():
                    project.external_accessions.add(existing_accession)
                continue

            external_accessions.append(ExternalAccession.get_from_dict(external_accession_data))

        ExternalAccession.objects.bulk_create(external_accessions)
        project.external_accessions.add(*external_accessions)
