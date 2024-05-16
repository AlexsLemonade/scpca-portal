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

    @staticmethod
    def bulk_create_from_project_data(project_data, project):
        """Creates a list of contact objects and then save them."""
        accessions = [
            a.strip()
            for a in project_data["external_accession"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        urls = [
            u.strip(common.STRIPPED_INPUT_VALUES)
            for u in project_data["external_accession_url"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        accessions_raw = [
            utils.boolean_from_string(ar.strip())
            for ar in project_data["external_accession_raw"].split(common.CSV_MULTI_VALUE_DELIMITER)
        ]
        external_accessions = []

        if len(set((len(accessions), len(urls), len(accessions_raw)))) != 1:
            logger.error("Unable to add ambiguous external accessions.")
            return

        for idx, accession in enumerate(accessions):
            if accession in common.IGNORED_INPUT_VALUES:
                continue

            # Skip if already in db
            if ExternalAccession.objects.filter(accession=accession):
                continue

            external_accession_data = {
                "accession": accession,
                "has_raw": accessions_raw[idx],
                "url": urls[idx],
            }

            external_accessions.append(ExternalAccession.get_from_dict(external_accession_data))

        ExternalAccession.objects.bulk_create(external_accessions)
        project.external_accessions.add(*external_accessions)
