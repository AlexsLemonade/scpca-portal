import csv
import json
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import connection, models
from django.template.defaultfilters import pluralize
from django.template.loader import render_to_string

from scpca_portal import common, utils
from scpca_portal.models.base import CommonDataAttributes, TimestampedModel
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.contact import Contact
from scpca_portal.models.external_accession import ExternalAccession
from scpca_portal.models.project_summary import ProjectSummary
from scpca_portal.models.publication import Publication
from scpca_portal.models.sample import Sample

logger = logging.getLogger()

IGNORED_INPUT_VALUES = {"", "N/A", "TBD"}
STRIPPED_INPUT_VALUES = "< >"


class Project(CommonDataAttributes, TimestampedModel):
    class Meta:
        db_table = "projects"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    abstract = models.TextField()
    additional_metadata_keys = models.TextField(blank=True, null=True)
    additional_restrictions = models.TextField(blank=True, null=True)
    diagnoses = models.TextField(blank=True, null=True)
    diagnoses_counts = models.TextField(blank=True, null=True)
    disease_timings = models.TextField()
    downloadable_sample_count = models.IntegerField(default=0)
    has_multiplexed_data = models.BooleanField(default=False)
    has_single_cell_data = models.BooleanField(default=False)
    has_spatial_data = models.BooleanField(default=False)
    human_readable_pi_name = models.TextField()
    includes_anndata = models.BooleanField(default=False)
    includes_cell_lines = models.BooleanField(default=False)
    includes_xenografts = models.BooleanField(default=False)
    modalities = ArrayField(models.TextField(), default=list)
    multiplexed_sample_count = models.IntegerField(default=0)
    organisms = ArrayField(models.TextField(), default=list)
    pi_name = models.TextField()
    sample_count = models.IntegerField(default=0)
    scpca_id = models.TextField(unique=True)
    seq_units = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    title = models.TextField()
    unavailable_samples_count = models.PositiveIntegerField(default=0)

    contacts = models.ManyToManyField(Contact)
    external_accessions = models.ManyToManyField(ExternalAccession)
    publications = models.ManyToManyField(Publication)

    def __str__(self):
        return f"Project {self.scpca_id}"

    @property
    def computed_files(self):
        return self.project_computed_files.order_by("created_at")

    @property
    def single_cell_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    # FOR TESTING
    @property
    def single_cell_anndata_computed_file(self):
        try:
            return self.project_computed_files.get(
                format=ComputedFile.OutputFileFormats.ANN_DATA,
                type=ComputedFile.OutputFileTypes.PROJECT_ZIP,
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def spatial_computed_file(self):
        try:
            return self.project_computed_files.get(
                type=ComputedFile.OutputFileTypes.PROJECT_SPATIAL_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass

    @property
    def multiplexed_computed_file(self):
        try:
            return self.project_computed_files.get(
                type=ComputedFile.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP
            )
        except ComputedFile.DoesNotExist:
            pass
    # END

    def add_contacts(self, contact_email, contact_name):
        """Creates and adds project contacts."""
        emails = contact_email.split(common.CSV_MULTI_VALUE_DELIMITER)
        names = contact_name.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(emails) != len(names):
            logger.error("Unable to add ambiguous contacts.")
            return

        for idx, email in enumerate(emails):
            if email in IGNORED_INPUT_VALUES:
                continue

            contact, _ = Contact.objects.get_or_create(email=email.lower().strip())
            contact.name = names[idx].strip()
            contact.submitter_id = self.pi_name
            contact.save()

            self.contacts.add(contact)

    def add_external_accessions(
        self, external_accession, external_accession_url, external_accession_raw
    ):
        """Creates and adds project external accessions."""
        accessions = external_accession.split(common.CSV_MULTI_VALUE_DELIMITER)
        urls = external_accession_url.split(common.CSV_MULTI_VALUE_DELIMITER)
        accessions_raw = external_accession_raw.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(set((len(accessions), len(urls), len(accessions_raw)))) != 1:
            logger.error("Unable to add ambiguous external accessions.")
            return

        for idx, accession in enumerate(accessions):
            if accession in IGNORED_INPUT_VALUES:
                continue

            external_accession, _ = ExternalAccession.objects.get_or_create(
                accession=accession.strip()
            )
            external_accession.url = urls[idx].strip(STRIPPED_INPUT_VALUES)
            external_accession.has_raw = utils.boolean_from_string(accessions_raw[idx].strip())
            external_accession.save()

            self.external_accessions.add(external_accession)

    def add_publications(self, citation, citation_doi):
        """Creates and adds project publications."""
        citations = citation.split(common.CSV_MULTI_VALUE_DELIMITER)
        dois = citation_doi.split(common.CSV_MULTI_VALUE_DELIMITER)

        if len(citations) != len(dois):
            logger.error("Unable to add ambiguous publications.")
            return

        for idx, doi in enumerate(dois):
            if doi in IGNORED_INPUT_VALUES:
                continue

            publication, _ = Publication.objects.get_or_create(doi=doi.strip())
            publication.citation = citations[idx].strip(STRIPPED_INPUT_VALUES)
            publication.submitter_id = self.pi_name
            publication.save()

            self.publications.add(publication)

    def get_samples(
        self,
        samples_metadata,
        multiplexed_sample_demux_cell_counter,
        multiplexed_sample_mapping,
        multiplexed_sample_seq_units_mapping,
        multiplexed_sample_technologies_mapping,
        sample_id=None,
    ):
        """Prepares ready for saving sample objects."""
        samples = []
        for sample_metadata in samples_metadata:
            scpca_sample_id = sample_metadata["scpca_sample_id"]
            if sample_id and scpca_sample_id != sample_id:
                continue
            sample_metadata[
                "demux_cell_count_estimate"
            ] = multiplexed_sample_demux_cell_counter.get(scpca_sample_id)
            sample_metadata["multiplexed_with"] = sorted(
                multiplexed_sample_mapping.get(scpca_sample_id, ())
            )
            sample_metadata["seq_units"] = (
                ", ".join(
                    sorted(
                        multiplexed_sample_seq_units_mapping.get(scpca_sample_id, ()), key=str.lower
                    )
                )
                or sample_metadata["seq_units"]
            )
            sample_metadata["technologies"] = (
                ", ".join(
                    sorted(
                        multiplexed_sample_technologies_mapping.get(scpca_sample_id, ()),
                        key=str.lower,
                    )
                )
                or sample_metadata["technologies"]
            )

            samples.append(Sample.get_from_dict(sample_metadata, self))

        return samples

    # TODO - 'purge from db' here, move 'purge from s3' elsewhere?
    def purge(self, delete_from_s3=False):
        """Purges project and its related data."""
        for sample in self.samples.all():
            for computed_file in sample.computed_files:
                if delete_from_s3:
                    computed_file.delete_s3_file(force=True)
                computed_file.delete()
            sample.delete()

        for computed_file in self.computed_files:
            if delete_from_s3:
                computed_file.delete_s3_file(force=True)
            computed_file.delete()

        ProjectSummary.objects.filter(project=self).delete()
        self.delete()

    def update_counts(self):
        """
        The Project and ProjectSummary models cache aggregated sample metadata.
        We need to update these after any project's sample gets added/deleted.
        """

        additional_metadata_keys = set()
        diagnoses = set()
        diagnoses_counts = Counter()
        disease_timings = set()
        modalities = set()
        organisms = set()
        seq_units = set()
        summaries_counts = Counter()
        technologies = set()

        for sample in self.samples.all():
            additional_metadata_keys.update(sample.additional_metadata.keys())
            diagnoses.add(sample.diagnosis)
            diagnoses_counts.update({sample.diagnosis: 1})
            disease_timings.add(sample.disease_timing)
            modalities.update(sample.modalities)
            if "organism" in sample.additional_metadata:
                organisms.add(sample.additional_metadata["organism"])

            sample_seq_units = sample.seq_units.split(", ")
            sample_technologies = sample.technologies.split(", ")
            for seq_unit in sample_seq_units:
                for technology in sample_technologies:
                    summaries_counts.update(
                        {(sample.diagnosis, seq_unit.strip(), technology.strip()): 1}
                    )

            seq_units.update(sample_seq_units)
            technologies.update(sample_technologies)

        diagnoses_strings = sorted(
            (f"{diagnosis} ({count})" for diagnosis, count in diagnoses_counts.items())
        )
        downloadable_sample_count = (
            self.samples.filter(sample_computed_files__isnull=False).distinct().count()
        )
        multiplexed_sample_count = self.samples.filter(has_multiplexed_data=True).count()
        non_downloadable_samples_count = self.samples.filter(
            has_multiplexed_data=False, has_single_cell_data=False, has_spatial_data=False
        ).count()
        sample_count = self.samples.count()
        seq_units = sorted((seq_unit for seq_unit in seq_units if seq_unit))
        technologies = sorted((technology for technology in technologies if technology))
        unavailable_samples_count = max(
            sample_count - downloadable_sample_count - non_downloadable_samples_count, 0
        )

        if self.has_multiplexed_data and "multiplexed_with" in additional_metadata_keys:
            additional_metadata_keys.remove("multiplexed_with")

        self.additional_metadata_keys = ", ".join(sorted(additional_metadata_keys, key=str.lower))
        self.diagnoses = ", ".join(sorted(diagnoses))
        self.diagnoses_counts = ", ".join(diagnoses_strings)
        self.disease_timings = ", ".join(disease_timings)
        self.downloadable_sample_count = downloadable_sample_count
        self.modalities = sorted(modalities)
        self.multiplexed_sample_count = multiplexed_sample_count
        self.organisms = sorted(organisms)
        self.sample_count = sample_count
        self.seq_units = ", ".join(seq_units)
        self.technologies = ", ".join(technologies)
        self.unavailable_samples_count = unavailable_samples_count
        self.save()

        for (diagnosis, seq_unit, technology), count in summaries_counts.items():
            project_summary, _ = ProjectSummary.objects.get_or_create(
                diagnosis=diagnosis, project=self, seq_unit=seq_unit, technology=technology
            )
            project_summary.sample_count = count
            project_summary.save(update_fields=("sample_count",))
