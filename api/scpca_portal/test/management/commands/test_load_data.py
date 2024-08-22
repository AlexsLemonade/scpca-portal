import csv
import re
import shutil
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from django.test import TransactionTestCase

from scpca_portal import common, metadata_file, readme_file, utils
from scpca_portal.management.commands.configure_aws_cli import Command as configure_aws_cli
from scpca_portal.management.commands.load_data import Command as load_data
from scpca_portal.models import ComputedFile, Project, ProjectSummary, Sample

# NOTE: Test data bucket is defined in `scpca_porta/common.py`.
# When common.INPUT_BUCKET_NAME is changed, please delete the contents of
# api/test_data/input before testing to ensure test files are updated correctly.

ALLOWED_SUBMITTERS = {"scpca"}

README_DIR = common.DATA_PATH / "readmes"
README_FILE = readme_file.OUTPUT_NAME


class TestLoadData(TransactionTestCase):
    def setUp(self):
        self.loader = load_data()
        configure_aws_cli()

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
        self.assertIsNotNone(project.seq_units)
        self.assertTrue(project.title)
        self.assertEqual(project.additional_restrictions, "Research or academic purposes only")

        project_summary = project.summaries.first()
        self.assertIsNotNone(project_summary.diagnosis)
        self.assertIsNotNone(project_summary.seq_unit)
        self.assertIsNotNone(project_summary.technology)

        sample = project.samples.first()
        self.assertIsNotNone(sample.age)
        self.assertIsNotNone(sample.age_timing)
        self.assertIsNotNone(sample.diagnosis)
        self.assertIsNotNone(sample.disease_timing)
        self.assertTrue(sample.scpca_id)
        self.assertIsNotNone(sample.sex)
        self.assertIsNotNone(sample.subdiagnosis)
        self.assertIsNotNone(sample.tissue_location)
        self.assertIsNotNone(sample.treatment)

    def assertProjectReadmeContent(self, zip_file, project_id=""):
        def get_updated_content(content):
            """
            Replace the placeholders PROJECT_ID and TEST_TODAYS_DATE in test_data/readmes
            with the given project_id and today's date respectively for format testing."
            """
            content = re.sub("PROJECT_ID", f"{project_id}", content)
            content = re.sub(
                "Generated on: TEST_TODAYS_DATE",
                f"Generated on: {utils.get_today_string()}",
                content,
            )

            return content.strip()

        # Get the corresponding saved readme output path based on the zip filename
        readme_filename = re.sub(r"^[A-Z\d]+_", "", Path(zip_file.filename).stem) + ".md"
        saved_readme_output_path = README_DIR / readme_filename
        # Convert expected and output contents to line lists for comparison
        with zip_file.open(README_FILE) as readme_file:
            output_content = readme_file.read().decode("utf-8").splitlines(True)
        with saved_readme_output_path.open("r", encoding="utf-8") as saved_readme_file:
            expected_content = get_updated_content(saved_readme_file.read()).splitlines(True)

        self.assertEqual(expected_content, output_content)

    @patch("scpca_portal.management.commands.load_data.Command.clean_up_output_data")
    @patch("scpca_portal.management.commands.load_data.Command.clean_up_input_data")
    def test_data_clean_up(self, mock_clean_up_input_data, mock_clean_up_output_data):
        project_id = "SCPCP999990"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=True,
            clean_up_output_data=True,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        mock_clean_up_input_data.assert_called_once()
        mock_clean_up_output_data.assert_called_once()

    def test_load_data(self):
        project_id = "SCPCP999990"

        def assert_object_count():
            self.assertEqual(Project.objects.count(), 1)
            self.assertEqual(ProjectSummary.objects.count(), 4)
            self.assertEqual(Sample.objects.count(), 4)
            # Expects 10 Computed Files
            samples = (2 * 2) + 1  # 2 Single-cell Samples in 2 formats and 1 spatial
            projects = 2 + 1  # Single-cell in 2 formats and 1 Spatial
            merged_projects = 1 * 2  # Merged SCE and merged AnnData
            metadata_only = 1  # 1 metadata only download per project
            expected_computed_files_count = samples + projects + merged_projects + metadata_only
            self.assertEqual(ComputedFile.objects.count(), expected_computed_files_count)

        # First, just test that loading data works.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

        project = Project.objects.get(scpca_id=project_id)
        project_computed_files = project.computed_files
        project_summary = project.summaries.first()
        sample = project.samples.first()
        sample_computed_files = sample.computed_files

        self.assertProjectData(project)

        # Make sure that reload_existing=False won't add anything new when there's nothing new.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

        new_project = Project.objects.get(scpca_id=project_id)
        self.assertEqual(project, new_project)
        self.assertEqual(project_summary, new_project.summaries.first())

        new_sample = new_project.samples.first()
        self.assertEqual(sample, new_sample)
        self.assertEqual(list(project_computed_files), list(new_project.computed_files))
        self.assertEqual(list(sample_computed_files), list(new_sample.computed_files))

        # Make sure purging works as expected.
        Project.objects.get(scpca_id=project_id).purge()

        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(ProjectSummary.objects.count(), 0)
        self.assertEqual(Sample.objects.count(), 0)
        self.assertEqual(ComputedFile.objects.count(), 0)

        # Make sure reloading works smoothly.
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=True,
            scpca_project_id=project_id,
            update_s3=False,
        )
        assert_object_count()

    def test_merged_project_anndata_cite_seq(self):
        project_id = "SCPCP999992"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertTrue(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertTrue(project.includes_merged_anndata)
        self.assertTrue(project.includes_merged_sce)

        self.assertGreater(project.single_cell_merged_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.single_cell_merged_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_merged_computed_file.includes_merged)
        self.assertTrue(project.single_cell_merged_computed_file.has_cite_seq_data)

        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )

        with ZipFile(project_zip_path) as project_zip:
            # There are 8 files:
            # ├── README.md
            # ├── SCPCP999992_merged-summary-report.html
            # ├── SCPCP999992_merged.rds
            # ├── individual_reports
            # │   ├── SCPCS999996
            # │   │   └── SCPCL999996_qc.html
            # │   │   └── SCPCL999996_celltype-report.html
            # │   └── SCPCS999998
            # │       └── SCPCL999998_qc.html
            # │       └── SCPCL999998_celltype-report.html
            # └── single_cell_metadata.tsv
            files = set(project_zip.namelist())
            self.assertEqual(len(files), 8)
            self.assertIn("SCPCP999992_merged.rds", files)
            self.assertNotIn("SCPCP999992_merged_adt.h5ad", files)
            self.assertProjectReadmeContent(project_zip, project_id)

        self.assertGreater(project.single_cell_anndata_merged_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.single_cell_anndata_merged_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_anndata_merged_computed_file.includes_merged)
        self.assertTrue(project.single_cell_anndata_merged_computed_file.has_cite_seq_data)
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "ANN_DATA",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            # There are 9 files:
            # ├── README.md
            # ├── SCPCP999992_merged-summary-report.html
            # ├── SCPCP999992_merged_adt.h5ad
            # ├── SCPCP999992_merged_rna.h5ad
            # ├── individual_reports
            # │   ├── SCPCS999996
            # │   │   └── SCPCL999996_qc.html
            # │   │   └── SCPCL999996_celltype-report.html
            # │   └── SCPCS999998
            # │       └── SCPCL999998_qc.html
            # │       └── SCPCL999998_celltype-report.html
            # └── single_cell_metadata.tsv
            files = set(project_zip.namelist())
            self.assertEqual(len(files), 9)
            self.assertIn("SCPCP999992_merged_rna.h5ad", files)
            self.assertIn("SCPCP999992_merged_adt.h5ad", files)
            self.assertProjectReadmeContent(project_zip, project_id)

    def test_merged_project_anndata_no_cite_seq(self):
        project_id = "SCPCP999990"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertTrue(project.includes_merged_anndata)
        self.assertTrue(project.includes_merged_sce)

        self.assertGreater(project.single_cell_merged_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.single_cell_merged_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_merged_computed_file.includes_merged)
        self.assertTrue(project.single_cell_merged_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.single_cell_merged_computed_file.has_cite_seq_data)
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            # There are 10 files:
            # ├── README.md
            # ├── SCPCP999990_merged-summary-report.html
            # ├── SCPCP999990_merged.rds
            # ├── bulk_metadata.tsv
            # ├── bulk_quant.tsv
            # ├── individual_reports
            # │   ├── SCPCS999990
            # │   │   └── SCPCL999990_qc.html
            # │   │   └── SCPCL999990_celltype-report.html
            # │   └── SCPCS999997
            # │       └── SCPCL999997_qc.html
            # │       └── SCPCL999997_celltype-report.html
            # └── single_cell_metadata.tsv
            files = set(project_zip.namelist())
            self.assertEqual(len(files), 10)
            self.assertIn("SCPCP999990_merged.rds", files)
            self.assertProjectReadmeContent(project_zip, project_id)

        self.assertGreater(project.single_cell_anndata_merged_computed_file.size_in_bytes, 0)
        self.assertEqual(
            project.single_cell_anndata_merged_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertTrue(project.single_cell_anndata_merged_computed_file.includes_merged)
        self.assertTrue(project.single_cell_anndata_merged_computed_file.has_bulk_rna_seq)
        self.assertFalse(project.single_cell_anndata_merged_computed_file.has_cite_seq_data)
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "ANN_DATA",
            "excludes_multiplexed": True,
            "includes_merged": True,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            # There are 10 files:
            # ├── README.md
            # ├── SCPCP999990_merged-summary-report.html
            # ├── SCPCP999990_merged_rna.h5ad
            # ├── bulk_metadata.tsv
            # ├── bulk_quant.tsv
            # ├── individual_reports
            # │   ├── SCPCS999990
            # │   │   └── SCPCL999990_qc.html
            # │   │   └── SCPCL999990_celltype-report.html
            # │   └── SCPCS999997
            # │       └── SCPCL999997_qc.html
            # │       └── SCPCL999997_celltype-report.html
            # └── single_cell_metadata.tsv
            files = set(project_zip.namelist())
            self.assertEqual(len(files), 10)
            self.assertIn("SCPCP999990_merged_rna.h5ad", files)
            self.assertProjectReadmeContent(project_zip, project_id)

    def test_no_merged_single_cell(self):
        project_id = "SCPCP999991"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertFalse(project.includes_merged_anndata)
        self.assertFalse(project.includes_merged_sce)
        self.assertIsNone(project.single_cell_merged_computed_file)
        self.assertIsNone(project.single_cell_anndata_merged_computed_file)
        single_cell = 2  # 1 computed file for AnnData and one for SCE
        multiplexed = 1  # 1 computed file for multiplexed
        merged = 0  # This project has no merged data for either format
        metadata_only = 1  # 1 metadata only download per project
        expected_computed_files = single_cell + multiplexed + merged + metadata_only
        self.assertEqual(project.computed_files.count(), expected_computed_files)

    def test_multiplexed_metadata(self):
        project_id = "SCPCP999991"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertFalse(project.has_bulk_rna_seq)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_multiplexed_data)
        self.assertEqual(project.multiplexed_sample_count, 2)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        self.assertEqual(project.sample_count, 3)
        self.assertEqual(project.summaries.count(), 3)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        # Expected Computed Files
        single_cell = 2  # 1 project x 2 formats
        multiplexed = 1  # 1 project x 1 multiplexed version
        metadata_only = 1  # 1 metadata only download per project
        expected_computed_files = single_cell + multiplexed + metadata_only
        self.assertEqual(len(project.computed_files), expected_computed_files)
        self.assertGreater(project.multiplexed_computed_file.size_in_bytes, 0)
        self.assertEqual(project.multiplexed_computed_file.workflow_version, "development")
        self.assertEqual(
            project.multiplexed_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertFalse(project.multiplexed_computed_file.has_bulk_rna_seq)
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

        expected_project_keys = [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "disease_timing",
            "age",
            "age_timing",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter_id",
            "organism",
            "development_stage_ontology_term_id",
            "sex_ontology_term_id",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "disease_ontology_term_id",
            "tissue_ontology_term_id",
            "WHO_grade",
            "seq_unit",
            "technology",
            "demux_samples",
            "total_reads",
            "mapped_reads",
            "sample_cell_count_estimate",  # with non-multiplexed
            "sample_cell_estimate",
            "unfiltered_cells",
            "filtered_cell_count",  # with non-multiplexed
            "processed_cells",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "pi_name",
            "project_title",
            "genome_assembly",
            "mapping_index",
            "alevin_fry_version",
            "salmon_version",
            "transcript_type",
            "droplet_filtering_method",
            "cell_filtering_method",
            "prob_compromised_cutoff",
            "min_gene_cutoff",
            "normalization_method",
            "demux_method",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
        ]

        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContent(project_zip, project_id)

        self.assertEqual(len(sample_metadata_lines), 4)  # 3 items + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_project_keys)

        # There are 12 files:
        # ├── README.md
        # ├── SCPCS999990
        # │   ├── SCPCL999990_celltype-report.html
        # │   ├── SCPCL999990_filtered.rds
        # │   ├── SCPCL999990_processed.rds
        # │   ├── SCPCL999990_qc.html
        # │   └── SCPCL999990_unfiltered.rds
        # ├── SCPCS999992_SCPCS999993
        # │   ├── SCPCL999992_celltype-report.html
        # │   ├── SCPCL999992_filtered.rds
        # │   ├── SCPCL999992_processed.rds
        # │   ├── SCPCL999992_qc.html
        # │   └── SCPCL999992_unfiltered.rds
        # └── single_cell_metadata.tsv

        self.assertEqual(len(project_zip.namelist()), 12)

        library_sample_mapping = {
            "SCPCL999992": "SCPCS999992_SCPCS999993",
            "SCPCL999995": "SCPCS999995",
        }
        library_path_templates = (
            "{sample_id}/{library_id}_celltype-report.html",
            "{sample_id}/{library_id}_filtered.rds",
            "{sample_id}/{library_id}_processed.rds",
            "{sample_id}/{library_id}_qc.html",
            "{sample_id}/{library_id}_unfiltered.rds",
        )
        expected_filenames = {
            "README.md",
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
        self.assertEqual(sample.seq_units, "nucleus")
        self.assertEqual(sample.technologies, "10Xv3.1")
        self.assertEqual(
            sample.multiplexed_computed_file.modality,
            ComputedFile.OutputFileModalities.SINGLE_CELL,
        )
        self.assertFalse(sample.multiplexed_computed_file.has_bulk_rna_seq)
        self.assertFalse(sample.multiplexed_computed_file.has_cite_seq_data)

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
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

        expected_sample_keys = [
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "disease_timing",
            "age",
            "age_timing",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter_id",
            "organism",
            "development_stage_ontology_term_id",
            "sex_ontology_term_id",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "disease_ontology_term_id",
            "tissue_ontology_term_id",
            "WHO_grade",
            "seq_unit",
            "technology",
            "demux_samples",
            "total_reads",
            "mapped_reads",
            "sample_cell_estimate",
            "unfiltered_cells",
            "filtered_cell_count",  # with non-multiplexed
            "processed_cells",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "pi_name",
            "project_title",
            "genome_assembly",
            "mapping_index",
            "alevin_fry_version",
            "salmon_version",
            "transcript_type",
            "droplet_filtering_method",
            "cell_filtering_method",
            "prob_compromised_cutoff",
            "min_gene_cutoff",
            "normalization_method",
            "demux_method",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
        ]
        # Check SingleCellExperiment archive.
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
        }
        sample_zip_path = common.OUTPUT_DATA_PATH / sample.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
            ) as sample_csv:
                csv_reader = csv.DictReader(
                    TextIOWrapper(sample_csv, "utf-8"), delimiter=common.TAB
                )
                rows = list(csv_reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(list(rows[0].keys()), expected_sample_keys)

        library_id = rows[0]["scpca_library_id"]
        expected_filenames = {
            "README.md",
            "single_cell_metadata.tsv",
            f"{library_id}_celltype-report.html",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    def test_single_cell_metadata(self):
        project_id = "SCPCP999990"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertEqual(project.downloadable_sample_count, 3)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.includes_anndata)
        self.assertTrue(project.modalities)
        self.assertEqual(project.multiplexed_sample_count, 0)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        # This project contains 3 samples
        single_cell = 2
        spatial = 1
        bulk = 1
        expected_samples = single_cell + spatial + bulk
        self.assertEqual(project.sample_count, expected_samples)
        self.assertFalse(project.has_multiplexed_data)
        self.assertEqual(project.sample_count, 4)
        self.assertEqual(project.seq_units, "cell, spot")
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        self.assertEqual(project.technologies, "10Xv3, visium")
        metadata_only = 1  # 1 metadata only download per project
        self.assertEqual(len(project.computed_files), (single_cell * 2) + spatial + metadata_only)
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
            "scpca_project_id",
            "scpca_sample_id",
            "scpca_library_id",
            "diagnosis",
            "subdiagnosis",
            "disease_timing",
            "age",
            "age_timing",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter_id",
            "organism",
            "development_stage_ontology_term_id",
            "sex_ontology_term_id",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "disease_ontology_term_id",
            "tissue_ontology_term_id",
            "WHO_grade",
            "seq_unit",
            "technology",
            "total_reads",
            "mapped_reads",
            "sample_cell_count_estimate",
            "unfiltered_cells",
            "filtered_cell_count",
            "processed_cells",
            "has_cellhash",
            "includes_anndata",
            "is_cell_line",
            "is_multiplexed",
            "is_xenograft",
            "pi_name",
            "project_title",
            "genome_assembly",
            "mapping_index",
            "alevin_fry_version",
            "salmon_version",
            "transcript_type",
            "droplet_filtering_method",
            "cell_filtering_method",
            "prob_compromised_cutoff",
            "min_gene_cutoff",
            "normalization_method",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
        ]

        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": False,
            "includes_merged": False,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            sample_metadata = project_zip.read(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContent(project_zip, project_id)

        self.assertEqual(len(sample_metadata_lines), 3)  # 2 items + header.

        sample_metadata_keys = sample_metadata_lines[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are 14 files:
        # ├── README.md
        # ├── SCPCS999990
        # │   ├── SCPCL999990_celltype-report.html
        # │   ├── SCPCL999990_filtered.rds
        # │   ├── SCPCL999990_processed.rds
        # │   ├── SCPCL999990_qc.html
        # │   └── SCPCL999990_unfiltered.rds
        # ├── SCPCS999997
        # │   ├── SCPCL999997_celltype-report.html
        # │   ├── SCPCL999997_filtered.rds
        # │   ├── SCPCL999997_processed.rds
        # │   ├── SCPCL999997_qc.html
        # │   └── SCPCL999997_unfiltered.rds
        # ├── bulk_metadata.tsv
        # ├── bulk_quant.tsv
        # └── single_cell_metadata.tsv

        self.assertEqual(len(project_zip.namelist()), 14)

        sample = project.samples.filter(has_single_cell_data=True).first()
        self.assertEqual(len(sample.computed_files), 2)
        self.assertIsNone(sample.demux_cell_count_estimate)
        self.assertFalse(sample.has_bulk_rna_seq)
        self.assertFalse(sample.has_cite_seq_data)
        # This line will probably fail when switching test data versions
        # The reason is that the filtered_cells attribute from the library json files,
        # from which sample_cell_count_estimate is calculated, changes from version to version
        self.assertEqual(sample.sample_cell_count_estimate, 3432)
        self.assertEqual(sample.seq_units, "cell")
        self.assertEqual(sample.technologies, "10Xv3")
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
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
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
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "SINGLE_CELL_EXPERIMENT",
        }
        sample_zip_path = common.OUTPUT_DATA_PATH / sample.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
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
            f"{library_id}_celltype-report.html",
            f"{library_id}_filtered.rds",
            f"{library_id}_processed.rds",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered.rds",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

        # Check AnnData archive.
        download_config = {
            "modality": "SINGLE_CELL",
            "format": "ANN_DATA",
        }
        sample_zip_path = common.OUTPUT_DATA_PATH / sample.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME, "r"
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
            f"{library_id}_celltype-report.html",
            f"{library_id}_filtered_rna.h5ad",
            f"{library_id}_processed_rna.h5ad",
            f"{library_id}_qc.html",
            f"{library_id}_unfiltered_rna.h5ad",
        }
        self.assertEqual(set(sample_zip.namelist()), expected_filenames)

    def test_spatial_metadata(self):
        project_id = "SCPCP999990"
        self.loader.load_data(
            allowed_submitters=ALLOWED_SUBMITTERS,
            clean_up_input_data=False,
            clean_up_output_data=False,
            max_workers=4,
            reload_all=False,
            reload_existing=False,
            scpca_project_id=project_id,
            update_s3=False,
        )

        project = Project.objects.get(scpca_id=project_id)
        self.assertProjectData(project)
        self.assertEqual(project.downloadable_sample_count, 3)
        self.assertFalse(project.has_cite_seq_data)
        self.assertTrue(project.has_spatial_data)
        self.assertTrue(project.modalities)
        self.assertEqual(project.organisms, ["Homo sapiens"])
        # Expected Samples
        single_cell = 2
        spatial = 1
        bulk = 1
        expected_samples = single_cell + spatial + bulk
        self.assertEqual(project.sample_count, expected_samples)
        self.assertEqual(project.summaries.count(), 4)
        self.assertEqual(project.summaries.first().sample_count, 1)
        self.assertEqual(project.unavailable_samples_count, 0)
        metadata_only = 1  # 1 metadata only download per project
        self.assertEqual(len(project.computed_files), 5 + metadata_only)
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
            "diagnosis",
            "subdiagnosis",
            "disease_timing",
            "age",
            "age_timing",
            "sex",
            "tissue_location",
            "participant_id",
            "submitter_id",
            "organism",
            "development_stage_ontology_term_id",
            "sex_ontology_term_id",
            "organism_ontology_id",
            "self_reported_ethnicity_ontology_term_id",
            "disease_ontology_term_id",
            "tissue_ontology_term_id",
            "WHO_grade",
            "seq_unit",
            "technology",
            "total_reads",
            "mapped_reads",
            "filtered_spots",
            "unfiltered_spots",
            "tissue_spots",
            "includes_anndata",
            "is_cell_line",
            "is_xenograft",
            "pi_name",
            "project_title",
            "genome_assembly",
            "mapping_index",
            "spaceranger_version",
            "date_processed",
            "workflow",
            "workflow_version",
            "workflow_commit",
        ]

        download_config = {
            "modality": "SPATIAL",
            "format": "SINGLE_CELL_EXPERIMENT",
            "excludes_multiplexed": True,
            "includes_merged": False,
            "metadata_only": False,
        }
        project_zip_path = common.OUTPUT_DATA_PATH / project.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(project_zip_path) as project_zip:
            spatial_metadata_file = project_zip.read(
                metadata_file.MetadataFilenames.SPATIAL_METADATA_FILE_NAME
            )
            spatial_metadata = [
                sm for sm in spatial_metadata_file.decode("utf-8").split("\r\n") if sm
            ]
            self.assertProjectReadmeContent(project_zip, project_id)

        self.assertEqual(len(spatial_metadata), 2)  # 1 item + header.

        sample_metadata_keys = spatial_metadata[0].split(common.TAB)
        self.assertEqual(sample_metadata_keys, expected_keys)

        # There are 16 files:
        # ├── README.md
        # ├── SCPCS999991
        # │   └── SCPCL999991_spatial
        # │       ├── SCPCL999991_metadata.json
        # │       ├── SCPCL999991_spaceranger-summary.html
        # │       ├── filtered_feature_bc_matrix
        # │       │   ├── barcodes.tsv.gz
        # │       │   ├── features.tsv.gz
        # │       │   └── matrix.mtx.gz
        # │       ├── raw_feature_bc_matrix
        # │       │   ├── barcodes.tsv.gz
        # │       │   ├── features.tsv.gz
        # │       │   └── matrix.mtx.gz
        # │       └── spatial
        # │           ├── aligned_fiducials.jpg
        # │           ├── detected_tissue_image.jpg
        # │           ├── scalefactors_json.json
        # │           ├── tissue_hires_image.png
        # │           ├── tissue_lowres_image.png
        # │           └── tissue_positions_list.csv
        # └── spatial_metadata.tsv
        self.assertEqual(len(project_zip.namelist()), 16)

        sample = project.samples.filter(has_spatial_data=True).first()
        self.assertEqual(len(sample.computed_files), 1)
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

        # Assert that single-cell modality computed files
        # do not get created when `has_single_cell_data` is False.
        self.assertFalse(sample.has_single_cell_data)
        self.assertFalse(
            sample.computed_files.filter(
                modality=ComputedFile.OutputFileModalities.SINGLE_CELL
            ).exists()
        )

        expected_additional_metadata_keys = [
            "development_stage_ontology_term_id",
            "disease_ontology_term_id",
            "organism",
            "organism_ontology_id",
            "participant_id",
            "self_reported_ethnicity_ontology_term_id",
            "sex_ontology_term_id",
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

        # Check Spatial archive.
        download_config = {
            "modality": "SPATIAL",
            "format": "SINGLE_CELL_EXPERIMENT",
        }
        sample_zip_path = common.OUTPUT_DATA_PATH / sample.get_download_config_file_output_name(
            download_config
        )
        with ZipFile(sample_zip_path) as sample_zip:
            with sample_zip.open(
                metadata_file.MetadataFilenames.SPATIAL_METADATA_FILE_NAME, "r"
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
            "{library_id}_spatial/{library_id}_spaceranger-summary.html",
            "{library_id}_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/features.tsv.gz",
            "{library_id}_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
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
