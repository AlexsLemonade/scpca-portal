import csv
import shutil
from io import TextIOWrapper
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TransactionTestCase

from scpca_portal import common
from scpca_portal.management.commands.load_data import Command
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample

ALLOWED_SUBMITTERS = {"genomics_10X"}
INPUT_BUCKET_NAME = "scpca-portal-public-test-inputs/project-metadata-changes"


class TestLoadData(TransactionTestCase):
    project_id = "SCPCP999990"

    def setUp(self):
        self.loader = Command()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def assertProjectData(self, project):
        self.assertTrue(project.abstract)
        self.assertIsNotNone(project.contacts)
        self.assertIsNotNone(project.diagnoses)
        self.assertIsNotNone(project.diagnoses_counts)
        self.assertTrue(project.disease_timings)
        self.assertTrue(project.has_multiplexed_data)
        self.assertTrue(project.has_single_cell_data)
        self.assertTrue(project.has_spatial_data)
        self.assertFalse(project.includes_cell_lines)
        self.assertFalse(project.includes_xenografts)
        self.assertIsNotNone(project.seq_units)
        self.assertTrue(project.title)
        self.assertEqual(project.additional_restrictions, "Research or academic purposes only")

        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)

        sample = project.samples.first()
        self.assertIsNotNone(sample.age_at_diagnosis)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.disease_timing)
        self.assertTrue(sample.scpca_id)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.treatment)

    def assertProjectReadmeContains(self, text, project_zip):
        self.assertIn(text, project_zip.read("README.md").decode("utf-8"))

    @patch("scpca_portal.models.computed_file.ComputedFile.create_s3_file", lambda *_, **__: None)
    def test_data_clean_up(self):
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=True,
            clean_up_output_data=True,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )
        self.assertEqual(len(list((common.INPUT_DATA_PATH / self.project_id).glob("*"))), 0)
        self.assertEqual(len(list(common.OUTPUT_DATA_PATH.glob("*"))), 0)

    @patch("scpca_portal.models.computed_file.ComputedFile.create_s3_file", lambda *_, **__: None)
    def test_load_data(self):
        def assert_object_count():
            self.assertEqual(Project.objects.count(), 1)
            self.assertEqual(ProjectSummary.objects.count(), 5)
            self.assertEqual(Sample.objects.count(), 5)
            self.assertEqual(ComputedFile.objects.count(), 10)

        # First, just test that loading data works.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )
        assert_object_count()

        project = Project.objects.get(scpca_id=self.project_id)
        project_computed_files = project.computed_files
        project_summary = project.summaries.first()
        sample = project.samples.first()
        sample_computed_files = sample.computed_files

        self.assertProjectData(project)

        # Make sure that reload_existing=False won't add anything new when there's nothing new.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )
        assert_object_count()

        new_project = Project.objects.get(scpca_id=self.project_id)
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())

        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)
        self.assertEqual(list(project_computed_files), list(new_project.computed_files))
        self.assertEqual(list(sample_computed_files), list(new_sample.computed_files))

        # Make sure purging works as expected.
        Project.objects.get(scpca_id=self.project_id).purge()

        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Make sure reloading works smoothly.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=True,
            update_s3=False,
        )
        assert_object_count()

    @patch("scpca_portal.models.computed_file.ComputedFile.create_s3_file", lambda *_, **__: None)
    def test_multiplexed_metadata(self):
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=True,
        )

        project = Project.objects.get(scpca_id=self.project_id)
        self.assertProjectData(project)
        self.assertEqual(project.downloadable_sample_count, 4)
        self.assertTrue(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_multiplexed_data)
        self.assertEqual(project.multiplexed_sample_count, 2)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        self.assertEqual(project.sample_count, 5)
        self.assertEqual(project.summaries.count(), 5)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(len(project.computed_files), 4)
        self.assertGreater(project.multiplexed_computed_file.size_in_bytes, 0)
        self.assertEqual(project.multiplexed_computed_file.workflow_version, "development")
        self.assertEqual(
            project.multiplexed_computed_file.modality,
            ComputedFile.OutputFileModalities.MULTIPLEXED,
        )
        self.assertTrue(project.multiplexed_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.multiplexed_computed_file.has_cite_seq_data)

        # Check contacts.
        self.assertEqual(project.contacts.count(), 2)
        contact1, contact2 = project.contacts.all()
        self.assertEqual(contact1.name, "{contact 1}")
        self.assertEqual(contact1.email, "{email contact 1}")
        self.assertEqual(contact2.name, "{contact 2}")
        self.assertEqual(contact2.email, "{email contact 2}")

        # Check external accessions.
        self.assertEqual(project.external_accessions.count(), 2)
        accession1, accession2 = project.external_accessions.all()
        self.assertEqual(accession1.accession, "{SRA project accession}")
        self.assertTrue(accession1.has_raw)
        self.assertEqual(accession1.url, "{SRA Run Selector URL}")
        self.assertEqual(accession2.accession, "{GEO series accession}")
        self.assertFalse(accession2.has_raw)
        self.assertEqual(accession2.url, "{GEO Series URL}")

        # Check publications.
        self.assertEqual(project.publications.count(), 2)
        publication, publication2 = project.publications.all()
        self.assertEqual(publication.doi, "{doi 1}")
        self.assertEqual(publication.citation, "{formatted citation 1}")
        self.assertEqual(publication2.doi, "{doi 2}")
        self.assertEqual(publication2.citation, "{formatted citation 2}")

        expected_keys = [
            "scpca_sample_id",
            "scpca_library_id",
            "scpca_project_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter",
            "submitter_id",
            "alevin_fry_version",
            "cell_filtering_method",
            "demux_method",
            "demux_samples",
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "droplet_filtering_method",
            "filtered_cells",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "min_gene_cutoff",
            "normalization_method",
            "organism",
            "organism_ontology_id",
            "prob_compromised_cutoff",
            "processed_cells",
            "salmon_version",
            "sample_cell_estimates",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "tissue_ontology_term_id",
            "transcript_type",
            "unfiltered_cells",
            "WHO_grade",
        ]

        project_zip_path = common.OUTPUT_DATA_PATH / project.output_multiplexed_computed_file_name
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContains(
                "This dataset is designated as research or academic purposes only.",
                project_zip,
            )

        self.assertEqual(len(sample_metadata_lines), 3)  # 2 items + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are 12 files (including subdirectory names):
        # ├── README.md
        # ├── SCPCS999990
        # │   ├── SCPCL999990_filtered.rds
        # │   ├── SCPCL999990_processed.rds
        # │   ├── SCPCL999990_qc.html
        # │   └── SCPCL999990_unfiltered.rds
        # ├── SCPCS999992_SCPCS999993
        # │   ├── SCPCL999992_filtered.rds
        # │   ├── SCPCL999992_processed.rds
        # │   ├── SCPCL999992_qc.html
        # │   └── SCPCL999992_unfiltered.rds
        # ├── bulk_metadata.tsv
        # ├── bulk_quant.tsv
        # └── single_cell_metadata.tsv
        self.assertEqual(len(project_zip.namelist()), 12)

        library_sample_mapping = {
            "SCPCL999990": "SCPCS999990",
            "SCPCL999992": "SCPCS999992_SCPCS999993",
        }
        library_path_templates = (
            "{sample_id}/{library_id}_filtered.rds",
            "{sample_id}/{library_id}_processed.rds",
            "{sample_id}/{library_id}_qc.html",
            "{sample_id}/{library_id}_unfiltered.rds",
        )
        expected_filenames = {
            "README.md",
            "bulk_metadata.tsv",
            "bulk_quant.tsv",
            "single_cell_metadata.tsv",
        }
        for library_id, sample_id in library_sample_mapping.items():
            for library_path in library_path_templates:
                expected_filenames.add(
                    library_path.format(library_id=library_id, sample_id=sample_id)
                )
        self.assertTrue(expected_filenames.issubset(set(project_zip.namelist())))

        sample = project.samples.filter(has_multiplexed_data=True).first()
        self.assertIsNone(sample.sample_cell_count_estimate)
        self.assertTrue(sample.has_multiplexed_data)
        self.assertEqual(sample.seq_units, "cell")
        self.assertEqual(sample.technologies, "10Xv3.1")
        self.assertEqual(
            sample.multiplexed_computed_file.modality,
            ComputedFile.OutputFileModalities.MULTIPLEXED,
        )
        self.assertFalse(sample.multiplexed_computed_file.has_bulk_rna_seq)
        self.assertFalse(sample.multiplexed_computed_file.has_cite_seq_data)

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "is_cell_line",
            "is_xenograft",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "scpca_project_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        sample_zip_path = common.OUTPUT_DATA_PATH / sample.output_multiplexed_computed_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    @patch("scpca_portal.models.computed_file.ComputedFile.create_s3_file", lambda *_, **__: None)
    def test_single_cell_metadata(self):
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=True,
        )

        project = Project.objects.get(scpca_id=self.project_id)
        self.assertProjectData(project)
        self.assertEqual(project.downloadable_sample_count, 4)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertTrue(project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 2)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        self.assertEqual(project.sample_count, 5)
        self.assertEqual(project.seq_units, "cell, spot")
        self.assertEqual(project.summaries.count(), 5)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(project.technologies, "10Xv3.1, visium")
        self.assertEqual(len(project.computed_files), 4)
        self.assertGreater(project.single_cell_computed_file.size_in_bytes, 0)
        self.assertEqual(project.single_cell_computed_file.workflow_version, "development")
        self.assertEqual(
            project.single_cell_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.single_cell_computed_file.has_cite_seq_data)

        self.assertEqual(
            project.single_cell_anndata_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_anndata_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.single_cell_anndata_computed_file.has_cite_seq_data)

        expected_keys = [
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "seq_unit",
            "technology",
            "sample_cell_count_estimate",
            "scpca_project_id",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "alevin_fry_version",
            "cell_filtering_method",
            "date_processed",
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "droplet_filtering_method",
            "filtered_cell_count",
            "genome_assembly",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "mapped_reads",
            "mapping_index",
            "min_gene_cutoff",
            "normalization_method",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "prob_compromised_cutoff",
            "processed_cells",
            "salmon_version",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter",
            "submitter_id",
            "tissue_ontology_term_id",
            "total_reads",
            "transcript_type",
            "unfiltered_cells",
            "WHO_grade",
            "workflow",
            "workflow_commit",
            "workflow_version",
        ]

        project_zip_path = common.OUTPUT_DATA_PATH / project.output_single_cell_computed_file_name
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContains(
                "This dataset is designated as research or academic purposes only.",
                project_zip,
            )

        self.assertEqual(len(sample_metadata_lines), 2)  # 1 item + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are 8 files (including subdirectory names):
        # ├── README.md
        # ├── SCPCS999990
        # │   ├── SCPCL999990_filtered.rds
        # │   ├── SCPCL999990_processed.rds
        # │   ├── SCPCL999990_qc.html
        # │   └── SCPCL999990_unfiltered.rds
        # ├── bulk_metadata.tsv
        # ├── bulk_quant.tsv
        # └── single_cell_metadata.tsv
        self.assertEqual(len(project_zip.namelist()), 8)

        sample = project.samples.filter(has_single_cell_data=True).first()
        self.assertEqual(len(sample.computed_files), 2)
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        self.assertEqual(sample.sample_cell_count_estimate, 1638)
        self.assertEqual(sample.seq_units, "cell")
        self.assertEqual(sample.technologies, "10Xv3.1")
        self.assertIsNotNone(sample.single_cell_computed_file)
        self.assertGreater(sample.single_cell_computed_file.size_in_bytes, 0)
        self.assertEqual(sample.single_cell_computed_file.workflow_version, "development")
        self.assertEqual(
            sample.single_cell_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertFalse(sample.single_cell_computed_file.has_bulk_rna_seq)
        self.assertFalse(sample.single_cell_computed_file.has_cite_seq_data)
        self.assertEqual(
            sample.single_cell_anndata_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertFalse(sample.single_cell_anndata_computed_file.has_bulk_rna_seq)
        self.assertFalse(sample.single_cell_anndata_computed_file.has_cite_seq_data)

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "is_cell_line",
            "is_xenograft",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "scpca_project_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        # Check SingleCellExperiment archive.
        sample_zip_path = common.OUTPUT_DATA_PATH / sample.output_single_cell_computed_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

        # Check AnnData archive.
        sample_zip_path = (
            common.OUTPUT_DATA_PATH / sample.output_single_cell_anndata_computed_file_name
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_filtered_rna.hdf5",
            f"{library_id}_processed_rna.hdf5",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered_rna.hdf5",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    @patch("scpca_portal.models.computed_file.ComputedFile.create_s3_file", lambda *_, **__: None)
    def test_spatial_metadata(self):
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            input_bucket_name=INPUT_BUCKET_NAME,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=True,
        )

        project = Project.objects.get(scpca_id=self.project_id)
        self.assertProjectData(project)
        self.assertEqual(project.downloadable_sample_count, 4)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_spatial_data)
        self.assertTrue(project.modalities)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        self.assertEqual(project.sample_count, 5)
        self.assertEqual(project.summaries.count(), 5)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(len(project.computed_files), 4)
        self.assertGreater(project.spatial_computed_file.size_in_bytes, 0)
        self.assertEqual(project.spatial_computed_file.workflow_version, "development")
        self.assertEqual(
            project.spatial_computed_file.modality,
            ComputedFile.OutputFileModalities.SPATIAL,
        )
        self.assertFalse(project.spatial_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.spatial_computed_file.has_cite_seq_data)

        expected_keys = [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "technology",
            "seq_unit",
            "total_reads",
            "mapped_reads",
            "genome_assembly",
            "mapping_index",
            "date_processed",
            "spaceranger_version",
            "workflow",
            "workflow_version",
            "workflow_commit",
            "diagnosis",
            "subdiagnosis",
            "pi_name",
            "project_title",
            "disease_timing",
            "age_at_diagnosis",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter",
            "submitter_id",
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "includes_anndata",
            "is_cell_line",
            "is_xenograft",
            "organism",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]

        project_zip_path = common.OUTPUT_DATA_PATH / project.output_spatial_computed_file_name
        with ZipFile(project_zip_path) as project_zip:
            spatial_metadata_file = project_zip.read(
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME
            )
            spatial_metadata = [
                sm for sm in spatial_metadata_file.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContains(
                "This dataset is designated as research or academic purposes only.",
                project_zip,
            )

        self.assertEqual(len(spatial_metadata), 2)  # 1 item + header.

        spatial_metadata_keys = spatial_metadata[0].split(common.TAB)
        self.assertEqual(spatial_metadata_keys, expected_keys)

        # There are 19 files (including subdirectory names):
        # ├── README.md
        # ├── SCPCL999991_spatial
        # │   ├── SCPCL999991_metadata.json
        # │   ├── SCPCL999991_spaceranger_summary.html
        # │   ├── filtered_feature_bc_matrix
        # │   │   ├── barcodes.tsv.gz
        # │   │   ├── features.tsv.gz
        # │   │   └── matrix.mtx.gz
        # │   ├── raw_feature_bc_matrix
        # │   │   ├── barcodes.tsv.gz
        # │   │   ├── features.tsv.gz
        # │   │   └── matrix.mtx.gz
        # │   └── spatial
        # │       ├── aligned_fiducials.jpg
        # │       ├── detected_tissue_image.jpg
        # │       ├── scalefactors_json.json
        # │       ├── tissue_hires_image.png
        # │       ├── tissue_lowres_image.png
        # │       └── tissue_positions_list.csv
        # └── spatial_metadata.tsv
        self.assertEqual(len(project_zip.namelist()), 19)

        sample = project.samples.filter(has_spatial_data=True).first()
        self.assertEqual(len(sample.computed_files), 2)
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        self.assertFalse(sample.has_multiplexed_data)
        self.assertTrue(sample.has_spatial_data)
        self.assertEqual(sample.seq_units, "spot")
        self.assertIsNotNone(sample.spatial_computed_file)
        self.assertGreater(sample.spatial_computed_file.size_in_bytes, 0)
        self.assertEqual(sample.spatial_computed_file.workflow_version, "development")
        self.assertEqual(sample.technologies, "visium")
        self.assertEqual(
            sample.spatial_computed_file.modality,
            ComputedFile.OutputFileModalities.SPATIAL,
        )
        self.assertFalse(sample.spatial_computed_file.has_bulk_rna_seq)
        self.assertFalse(sample.spatial_computed_file.has_cite_seq_data)

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "is_cell_line",
            "is_xenograft",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "scpca_project_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
            "submitter",
            "submitter_id",
            "tissue_ontology_term_id",
            "WHO_grade",
        ]
        self.assertEqual(
            expected_additional_metadata_keys, project.additional_metadata_keys.split(", ")
        )
        self.assertEqual(
            set(expected_additional_metadata_keys), set(sample.additional_metadata.keys())
        )

        sample_zip_path = common.OUTPUT_DATA_PATH / sample.output_spatial_computed_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), expected_keys)

        library_ids = (rows[0]["scpca_library_id"],)
        expected_filenames = {
            "README.md",
            "spatial_metadata.tsv",
        }
        library_path_templates = {
            "{library_id}_spatial/{library_id}_metadata.json",
            "{library_id}_spatial/{library_id}_spaceranger_summary.html",
            "{library_id}_spatial/filtered_feature_bc_matrix/",
            "{library_id}_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/",
            "{library_id}_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
            "{library_id}_spatial/spatial/",
            "{library_id}_spatial/spatial/aligned_fiducials.jpg",
            "{library_id}_spatial/spatial/detected_tissue_image.jpg",
            "{library_id}_spatial/spatial/scalefactors_json.json",
            "{library_id}_spatial/spatial/tissue_hires_image.png",
            "{library_id}_spatial/spatial/tissue_lowres_image.png",
            "{library_id}_spatial/spatial/tissue_positions_list.csv",
        }
        for library_id in library_ids:
            for library_path in library_path_templates:
                expected_filenames.add(library_path.format(library_id=library_id))
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)
