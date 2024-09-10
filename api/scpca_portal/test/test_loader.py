import io
from csv import DictReader
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Set
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.test import TransactionTestCase

from scpca_portal import common, loader
from scpca_portal.models import Project
from scpca_portal.models.computed_file import ComputedFile
from scpca_portal.models.library import Library
from scpca_portal.models.sample import Sample


class TestLoader(TransactionTestCase):
    def setUp(self):
        self.get_projects_metadata = partial(
            loader.get_projects_metadata, input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME
        )
        # When passing a project_id to get_projects_metadata, a list of one item is returned
        # This lambda creates a shorthand with which to access the single returned project_metadata
        self.get_project_metadata = lambda project_id: self.get_projects_metadata(
            filter_on_project_id=project_id
        )[0]

        self.create_project = partial(
            loader.create_project,
            submitter_whitelist={"scpca"},
            input_bucket_name=settings.AWS_S3_INPUT_BUCKET_NAME,
            reload_existing=True,
            update_s3=False,
        )

        self.generate_computed_files = partial(
            loader.generate_computed_files,
            max_workers=10,
            update_s3=False,
            clean_up_output_data=False,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # shutil.rmtree(common.OUTPUT_DATA_PATH, ignore_errors=True)

    def assertObjectProperties(self, obj: Any, expected_values: Dict[str, Any]) -> None:
        for attribute, value in expected_values.items():
            msg = f"The actual and expected {attribute} values differ in {obj}"
            if isinstance(value, list):
                self.assertListEqual(getattr(obj, attribute), value, msg)
            else:
                self.assertEqual(getattr(obj, attribute), value, msg)

    def assertDictIsNonEmpty(self, d: Dict) -> None:
        self.assertTrue(any(key for key in d))

    def purge_extra_samples(self, project: Project, sample_of_interest: str) -> None:
        """Purges all of a project's samples that are not the sample of interest."""
        for sample in project.samples.all():
            if sample != sample_of_interest:
                sample.purge()

    def get_computed_files_query_params_from_download_config(self, download_config: Dict) -> Dict:
        if download_config.get("metadata_only"):
            return {"metadata_only": download_config["metadata_only"]}

        query_params = {
            "modality": download_config["modality"],
            "format": download_config["format"],
        }

        if download_config in common.SAMPLE_DOWNLOAD_CONFIGS.values():
            return query_params

        query_params["has_multiplexed_data"] = not download_config["excludes_multiplexed"]
        query_params["includes_merged"] = download_config["includes_merged"]

        return query_params

    def assertCorrectLibraries(self, project_zip: ZipFile, expected_libraries: Set[str]) -> None:
        self.assertCorrectLibrariesMetadata(project_zip, expected_libraries)
        self.assertCorrectLibrariesDataFiles(project_zip.namelist(), expected_libraries)

    def assertCorrectLibrariesMetadata(
        self, project_zip: ZipFile, expected_libraries: Set[str]
    ) -> None:
        file_list = project_zip.namelist()

        # Check via metadata file
        metadata_file_name = next(file_name for file_name in file_list if "metadata" in file_name)
        metadata_file = project_zip.read(metadata_file_name)
        metadata_file_str = io.StringIO(metadata_file.decode("utf-8"))
        metadata_file_dict_reader = DictReader(metadata_file_str, delimiter="\t")

        metadata_file_libraries = set(row["scpca_library_id"] for row in metadata_file_dict_reader)
        self.assertEqual(expected_libraries, metadata_file_libraries)

    def assertCorrectLibrariesDataFiles(
        self, file_list: List[str], expected_libraries: Set[str]
    ) -> None:
        data_file_paths = [Path(file) for file in file_list]
        data_file_libraries = set(
            # data files have paths that look like "SCPCS999990/SCPCL999990_processed.rds"
            file_path.name.split("_")[0]
            for file_path in data_file_paths
            if file_path.name.startswith("SCPCL")
        )
        self.assertEqual(expected_libraries, data_file_libraries)

    def assertProjectReadmeContains(self, text, project_zip):
        self.assertIn(text, project_zip.read("README.md").decode("utf-8"))

    def test_create_project_SCPCP999990(self):
        loader.prep_data_dirs()

        project_id = "SCPCP999990"
        returned_project = self.create_project(self.get_project_metadata(project_id))

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=project_id).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        expected_project_attribute_values = {
            "abstract": "TBD",
            "additional_restrictions": "Research or academic purposes only",
            "data_file_paths": [
                "SCPCP999990/merged/SCPCP999990_merged-summary-report.html",
                "SCPCP999990/merged/SCPCP999990_merged.rds",
                "SCPCP999990/merged/SCPCP999990_merged_rna.h5ad",
                "SCPCP999990/bulk/SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990/bulk/SCPCP999990_bulk_quant.tsv",
            ],
            "diagnoses": "diagnosis1, diagnosis2, diagnosis5, diagnosis8",
            "diagnoses_counts": "diagnosis1 (1), diagnosis2 (1), diagnosis5 (1), diagnosis8 (1)",
            "disease_timings": "Initial diagnosis",
            # This value is not determined until after computed file generation, and should be 3
            "downloadable_sample_count": 0,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": True,
            "human_readable_pi_name": "TBD",
            "includes_anndata": True,
            "includes_cell_lines": False,
            "includes_merged_sce": True,
            "includes_merged_anndata": True,
            "includes_xenografts": False,
            "modalities": [
                Sample.Modalities.NAME_MAPPING["BULK_RNA_SEQ"],
                Sample.Modalities.NAME_MAPPING["SPATIAL"],
            ],
            "multiplexed_sample_count": 0,
            "organisms": ["Homo sapiens"],
            "pi_name": "scpca",
            "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
            "sample_count": 4,
            "scpca_id": project_id,
            "seq_units": "cell, spot",
            "technologies": "10Xv3, visium",
            "title": "TBD",
            # unavailable_samples_count should be 1 here, but is returning the default 0.
            # This is due to the fact that it's not being assigned until after comp file generation.
            # This should be updated when the bug is handled.
            # "unavailable_samples_count": 1
        }
        self.assertObjectProperties(project, expected_project_attribute_values)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 4)

        # SCPCS999990
        sample_id = "SCPCS999990"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis1",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 3432,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv3",
            "tissue_location": "tissue1",
            "treatment": "",
        }
        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999991
        sample_id = "SCPCS999991"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis2",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": False,
            "has_spatial_data": True,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 0,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "spot",
            "subdiagnosis": "NA",
            "technologies": "visium",
            "tissue_location": "tissue2",
            "treatment": "",
        }

        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999994
        sample_id = "SCPCS999994"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis5",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": False,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 0,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "",
            "subdiagnosis": "NA",
            "technologies": "",
            "tissue_location": "tissue5",
            "treatment": "",
        }

        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999997
        sample_id = "SCPCS999997"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "collection",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis8",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 1568,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv3",
            "tissue_location": "tissue8",
            "treatment": "",
        }

        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 3)

        # SCPCL999990
        library_id = "SCPCL999990"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999990/SCPCS999990/SCPCL999990_celltype-report.html",
                "SCPCP999990/SCPCS999990/SCPCL999990_filtered.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_filtered_rna.h5ad",
                "SCPCP999990/SCPCS999990/SCPCL999990_processed.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_processed_rna.h5ad",
                "SCPCP999990/SCPCS999990/SCPCL999990_qc.html",
                "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered.rds",
                "SCPCP999990/SCPCS999990/SCPCL999990_unfiltered_rna.h5ad",
            ],
            "formats": [
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
                Library.FileFormats.ANN_DATA,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }

        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999991
        library_id = "SCPCL999991"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",  # noqa
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png",
                "SCPCP999990/SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv",
            ],
            "formats": [
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SPATIAL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }

        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999997
        library_id = "SCPCL999997"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999990/SCPCS999997/SCPCL999997_celltype-report.html",
                "SCPCP999990/SCPCS999997/SCPCL999997_filtered.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_filtered_rna.h5ad",
                "SCPCP999990/SCPCS999997/SCPCL999997_processed.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_processed_rna.h5ad",
                "SCPCP999990/SCPCS999997/SCPCL999997_qc.html",
                "SCPCP999990/SCPCS999997/SCPCL999997_unfiltered.rds",
                "SCPCP999990/SCPCS999997/SCPCL999997_unfiltered_rna.h5ad",
            ],
            "formats": [
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
                Library.FileFormats.ANN_DATA,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }

        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 4)

        # First project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis1",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Second project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis2",
            "sample_count": 1,
            "seq_unit": "spot",
            "technology": "visium",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Third project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis5",
            "sample_count": 1,
            "seq_unit": "",
            "technology": "",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Fourth project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis8",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        email = "{email contact 1}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 1}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # Second contact
        email = "{email contact 2}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 2}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        accession = "{SRA project accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": True,
            "url": "{SRA Run Selector URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # Second external accession
        accession = "{GEO series accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": False,
            "url": "{GEO Series URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        doi = "{doi 1}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 1}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

        # Second publication
        doi = "{doi 2}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 2}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

    def test_create_project_SCPCP999991(self):
        loader.prep_data_dirs()

        project_id = "SCPCP999991"
        returned_project = self.create_project(self.get_project_metadata(project_id))

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=project_id).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        expected_project_attribute_values = {
            "abstract": "TBD",
            "additional_restrictions": "Research or academic purposes only",
            "data_file_paths": [],
            "diagnoses": "diagnosis3, diagnosis4, diagnosis6",
            "diagnoses_counts": "diagnosis3 (1), diagnosis4 (1), diagnosis6 (1)",
            "disease_timings": "Initial diagnosis",
            # This value is not determined until after computed file generation, and should be 2
            "downloadable_sample_count": 0,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "human_readable_pi_name": "TBD",
            "includes_anndata": True,
            "includes_cell_lines": False,
            "includes_merged_sce": False,
            "includes_merged_anndata": False,
            "includes_xenografts": False,
            "modalities": [
                Sample.Modalities.NAME_MAPPING["MULTIPLEXED"],
            ],
            "multiplexed_sample_count": 2,
            "organisms": ["Homo sapiens"],
            "pi_name": "scpca",
            "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
            "sample_count": 3,
            "scpca_id": project_id,
            "seq_units": "cell, nucleus",
            "technologies": "10Xv3, 10Xv3.1",
            "title": "TBD",
            # unavailable_samples_count should be 1 here, but is returning the default 0.
            # This is due to the fact that it's not being assigned until after comp file generation.
            # This should be updated when the bug is handled.
            "unavailable_samples_count": 0,
        }

        self.assertObjectProperties(project, expected_project_attribute_values)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 3)

        # SCPCS999992
        sample_id = "SCPCS999992"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate": 0,
            "diagnosis": "diagnosis3",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": ["SCPCS999993"],
            "sample_cell_count_estimate": None,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "nucleus",
            "subdiagnosis": "NA",
            "technologies": "10Xv3.1",
            "tissue_location": "tissue3",
            "treatment": "",
        }

        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999993
        sample_id = "SCPCS999993"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate": 0,
            "diagnosis": "diagnosis4",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": False,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": ["SCPCS999992"],
            "sample_cell_count_estimate": None,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "nucleus",
            "subdiagnosis": "NA",
            "technologies": "10Xv3.1",
            "tissue_location": "tissue4",
            "treatment": "",
        }

        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999995
        sample_id = "SCPCS999995"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis6",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 3433,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv3",
            "tissue_location": "tissue6",
            "treatment": "",
        }
        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 2)

        # SCPCL999992
        library_id = "SCPCL999992"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_celltype-report.html",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_filtered.rds",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_processed.rds",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_qc.html",
                "SCPCP999991/SCPCS999992,SCPCS999993/SCPCL999992_unfiltered.rds",
            ],
            "formats": [
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": True,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }

        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999995
        library_id = "SCPCL999995"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999991/SCPCS999995/SCPCL999995_celltype-report.html",
                "SCPCP999991/SCPCS999995/SCPCL999995_filtered.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_filtered_rna.h5ad",
                "SCPCP999991/SCPCS999995/SCPCL999995_processed.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_processed_rna.h5ad",
                "SCPCP999991/SCPCS999995/SCPCL999995_qc.html",
                "SCPCP999991/SCPCS999995/SCPCL999995_unfiltered.rds",
                "SCPCP999991/SCPCS999995/SCPCL999995_unfiltered_rna.h5ad",
            ],
            "formats": [Library.FileFormats.SINGLE_CELL_EXPERIMENT, Library.FileFormats.ANN_DATA],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }

        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 3)

        # First project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis3",
            "sample_count": 1,
            "seq_unit": "nucleus",
            "technology": "10Xv3.1",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Second project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis4",
            "sample_count": 1,
            "seq_unit": "nucleus",
            "technology": "10Xv3.1",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Third project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis6",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        email = "{email contact 1}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 1}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # Second contact
        email = "{email contact 2}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 2}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        accession = "{SRA project accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": True,
            "url": "{SRA Run Selector URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # Second external accession
        accession = "{GEO series accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": False,
            "url": "{GEO Series URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        doi = "{doi 1}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 1}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

        # Second publication
        doi = "{doi 2}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 2}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

    def test_create_project_SCPCP999992(self):
        loader.prep_data_dirs()

        project_id = "SCPCP999992"
        returned_project = self.create_project(self.get_project_metadata(project_id))

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=project_id).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        expected_project_attribute_values = {
            "abstract": "TBD",
            "additional_restrictions": "Research or academic purposes only",
            "data_file_paths": [
                "SCPCP999992/merged/SCPCP999992_merged-summary-report.html",
                "SCPCP999992/merged/SCPCP999992_merged.rds",
                "SCPCP999992/merged/SCPCP999992_merged_adt.h5ad",
                "SCPCP999992/merged/SCPCP999992_merged_rna.h5ad",
            ],
            "diagnoses": "diagnosis7, diagnosis9",
            "diagnoses_counts": "diagnosis7 (1), diagnosis9 (1)",
            "disease_timings": "Initial diagnosis",
            # This value is not determined until after computed file generation, and should be 2
            "downloadable_sample_count": 0,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": True,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "human_readable_pi_name": "TBD",
            "includes_anndata": True,
            "includes_cell_lines": False,
            "includes_merged_sce": True,
            "includes_merged_anndata": True,
            "includes_xenografts": False,
            "modalities": [
                Sample.Modalities.NAME_MAPPING["CITE_SEQ"],
            ],
            "multiplexed_sample_count": 0,
            "organisms": ["Homo sapiens"],
            "pi_name": "scpca",
            "s3_input_bucket": settings.AWS_S3_INPUT_BUCKET_NAME,
            "sample_count": 2,
            "scpca_id": project_id,
            "seq_units": "cell",
            "technologies": "10Xv2_5prime, 10Xv3",
            "title": "TBD",
            # unavailable_samples_count should be 1 here, but is returning the default 0.
            # This is due to the fact that it's not being assigned until after comp file generation.
            # This should be updated when the bug is handled.
            "unavailable_samples_count": 0,
        }
        self.assertObjectProperties(project, expected_project_attribute_values)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 2)

        # SCPCS999996
        sample_id = "SCPCS999996"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "diagnosis",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis7",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 3425,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv3",
            "tissue_location": "tissue7",
            "treatment": "",
        }
        self.assertObjectProperties(sample, expected_sample_attribute_values)

        # SCPCS999998
        sample_id = "SCPCS999998"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        expected_sample_attribute_values = {
            "age": "2",
            "age_timing": "unknown",
            "demux_cell_count_estimate": None,
            "diagnosis": "diagnosis9",
            "disease_timing": "Initial diagnosis",
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": True,
            "has_multiplexed_data": False,
            "has_single_cell_data": True,
            "has_spatial_data": False,
            "includes_anndata": True,
            "is_cell_line": False,
            "is_xenograft": False,
            "multiplexed_with": [],
            "sample_cell_count_estimate": 52455,
            "scpca_id": sample_id,
            "sex": "M",
            "seq_units": "cell",
            "subdiagnosis": "NA",
            "technologies": "10Xv2_5prime",
            "tissue_location": "tissue9",
            "treatment": "",
        }

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 2)

        # SCPCL999996
        library_id = "SCPCL999996"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999992/SCPCS999996/SCPCL999996_celltype-report.html",
                "SCPCP999992/SCPCS999996/SCPCL999996_filtered.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_filtered_rna.h5ad",
                "SCPCP999992/SCPCS999996/SCPCL999996_processed.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_processed_rna.h5ad",
                "SCPCP999992/SCPCS999996/SCPCL999996_qc.html",
                "SCPCP999992/SCPCS999996/SCPCL999996_unfiltered.rds",
                "SCPCP999992/SCPCS999996/SCPCL999996_unfiltered_rna.h5ad",
            ],
            "formats": [
                Library.FileFormats.SINGLE_CELL_EXPERIMENT,
                Library.FileFormats.ANN_DATA,
            ],
            "has_cite_seq_data": False,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }
        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999998
        library_id = "SCPCL999998"
        library = project.libraries.filter(scpca_id=library_id).first()
        self.assertIsNotNone(library)

        expected_library_attribute_values = {
            "data_file_paths": [
                "SCPCP999992/SCPCS999998/SCPCL999998_celltype-report.html",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_filtered_rna.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_processed_rna.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_qc.html",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered.rds",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered_adt.h5ad",
                "SCPCP999992/SCPCS999998/SCPCL999998_unfiltered_rna.h5ad",
            ],
            "formats": [Library.FileFormats.SINGLE_CELL_EXPERIMENT, Library.FileFormats.ANN_DATA],
            "has_cite_seq_data": True,
            "is_multiplexed": False,
            "modality": Library.Modalities.SINGLE_CELL,
            "scpca_id": library_id,
            "workflow_version": "development",
        }
        self.assertObjectProperties(library, expected_library_attribute_values)
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 2)

        # First project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis7",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # Second project summary
        expected_summary_attribute_values = {
            "diagnosis": "diagnosis9",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv2_5prime",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        email = "{email contact 1}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 1}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # Second contact
        email = "{email contact 2}"
        contact = project.contacts.filter(email=email).first()
        self.assertIsNotNone(contact)

        expected_contact_attribute_values = {
            "name": "{contact 2}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        accession = "{SRA project accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": True,
            "url": "{SRA Run Selector URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # Second external accession
        accession = "{GEO series accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        self.assertIsNotNone(external_accession)

        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": False,
            "url": "{GEO Series URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        doi = "{doi 1}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 1}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

        # Second publication
        doi = "{doi 2}"
        publication = project.publications.filter(doi=doi).first()
        self.assertIsNotNone(publication)

        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 2}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999997"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "SCPCS999990/SCPCL999990_celltype-report.html",
                "SCPCS999990/SCPCL999990_filtered.rds",
                "SCPCS999990/SCPCL999990_processed.rds",
                "SCPCS999990/SCPCL999990_qc.html",
                "SCPCS999990/SCPCL999990_unfiltered.rds",
                "SCPCS999997/SCPCL999997_celltype-report.html",
                "SCPCS999997/SCPCL999997_filtered.rds",
                "SCPCS999997/SCPCL999997_processed.rds",
                "SCPCS999997/SCPCL999997_qc.html",
                "SCPCS999997/SCPCL999997_unfiltered.rds",
                # Do we want bulk files to be prefixed with the project id?
                "SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990_bulk_quant.tsv",
                "single_cell_metadata.tsv",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 9078,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999991"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999992", "SCPCL999995"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "single_cell_metadata.tsv",
                "SCPCS999995/SCPCL999995_celltype-report.html",
                "SCPCS999995/SCPCL999995_filtered.rds",
                "SCPCS999995/SCPCL999995_processed.rds",
                "SCPCS999995/SCPCL999995_qc.html",
                "SCPCS999995/SCPCL999995_unfiltered.rds",
                "SCPCS999992_SCPCS999993/SCPCL999992_celltype-report.html",
                "SCPCS999992_SCPCS999993/SCPCL999992_filtered.rds",
                "SCPCS999992_SCPCS999993/SCPCL999992_processed.rds",
                "SCPCS999992_SCPCS999993/SCPCL999992_qc.html",
                "SCPCS999992_SCPCS999993/SCPCL999992_unfiltered.rds",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": True,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 6594,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999997"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "single_cell_metadata.tsv",
                "individual_reports/SCPCS999990/SCPCL999990_celltype-report.html",
                "individual_reports/SCPCS999990/SCPCL999990_qc.html",
                "individual_reports/SCPCS999997/SCPCL999997_celltype-report.html",
                "individual_reports/SCPCS999997/SCPCL999997_qc.html",
                "SCPCP999990_merged-summary-report.html",
                "SCPCP999990_merged.rds",
                "SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990_bulk_quant.tsv",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": True,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 8476,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SINGLE_CELL_ANN_DATA"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999997"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "SCPCS999990/SCPCL999990_celltype-report.html",
                "SCPCS999990/SCPCL999990_filtered_rna.h5ad",
                "SCPCS999990/SCPCL999990_processed_rna.h5ad",
                "SCPCS999990/SCPCL999990_qc.html",
                "SCPCS999990/SCPCL999990_unfiltered_rna.h5ad",
                "SCPCS999997/SCPCL999997_celltype-report.html",
                "SCPCS999997/SCPCL999997_filtered_rna.h5ad",
                "SCPCS999997/SCPCL999997_processed_rna.h5ad",
                "SCPCS999997/SCPCL999997_qc.html",
                "SCPCS999997/SCPCL999997_unfiltered_rna.h5ad",
                # Do we want bulk files to be prefixed with the project id?
                "SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990_bulk_quant.tsv",
                "single_cell_metadata.tsv",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 9492,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA_MERGED(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SINGLE_CELL_ANN_DATA_MERGED"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999997"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "individual_reports/SCPCS999990/SCPCL999990_celltype-report.html",
                "individual_reports/SCPCS999990/SCPCL999990_qc.html",
                "individual_reports/SCPCS999997/SCPCL999997_celltype-report.html",
                "individual_reports/SCPCS999997/SCPCL999997_qc.html",
                # Do we want bulk files to be prefixed with the project id?
                "SCPCP999990_merged-summary-report.html",
                "SCPCP999990_merged_rna.h5ad",
                "SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990_bulk_quant.tsv",
                "single_cell_metadata.tsv",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": True,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": True,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 8601,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "SPATIAL_SINGLE_CELL_EXPERIMENT"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999991"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "spatial_metadata.tsv",
                "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",
                "SCPCS999991/SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
                "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",
                "SCPCS999991/SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
                "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
                "SCPCS999991/SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
                "SCPCS999991/SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
                "SCPCS999991/SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
                "SCPCS999991/SCPCL999991_spatial/spatial/scalefactors_json.json",
                "SCPCS999991/SCPCL999991_spatial/spatial/tissue_hires_image.png",
                "SCPCS999991/SCPCL999991_spatial/spatial/tissue_lowres_image.png",
                "SCPCS999991/SCPCL999991_spatial/spatial/tissue_positions_list.csv",
                "SCPCS999991/SCPCL999991_spatial/SCPCL999991_metadata.json",
            ]

            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SPATIAL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 9156,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_project_generate_computed_files_ALL_METADATA(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        download_config_name = "ALL_METADATA"
        download_config = common.PROJECT_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", [download_config]):
            with patch("scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", []):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999991", "SCPCL999997"}
            self.assertCorrectLibrariesMetadata(project_zip, expected_libraries)
            expected_file_list = ["README.md", "metadata.tsv"]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": None,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": None,
            "metadata_only": True,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 4866,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        sample_id = "SCPCS999990"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        download_config_name = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        download_config = common.SAMPLE_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", []):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, sample)
            with patch(
                "scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", [download_config]
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_download_config_file_output_name(download_config)
        sample_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990"}
            self.assertCorrectLibraries(sample_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "single_cell_metadata.tsv",
                "SCPCL999990_celltype-report.html",
                "SCPCL999990_filtered.rds",
                "SCPCL999990_processed.rds",
                "SCPCL999990_qc.html",
                "SCPCL999990_unfiltered.rds",
            ]
            result_file_list = sample_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 7017,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_sample_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        sample_id = "SCPCS999990"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        download_config_name = "SINGLE_CELL_ANN_DATA"
        download_config = common.SAMPLE_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", []):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, sample)
            with patch(
                "scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", [download_config]
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_download_config_file_output_name(download_config)
        sample_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990"}
            self.assertCorrectLibraries(sample_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "single_cell_metadata.tsv",
                "SCPCL999990_celltype-report.html",
                "SCPCL999990_filtered_rna.h5ad",
                "SCPCL999990_processed_rna.h5ad",
                "SCPCL999990_qc.html",
                "SCPCL999990_unfiltered_rna.h5ad",
            ]
            result_file_list = sample_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.ANN_DATA,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SINGLE_CELL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 7401,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)

    def test_sample_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        loader.prep_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        sample_id = "SCPCS999991"
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(sample)

        download_config_name = "SPATIAL_SINGLE_CELL_EXPERIMENT"
        download_config = common.SAMPLE_DOWNLOAD_CONFIGS[download_config_name]
        with patch("scpca_portal.common.PRE_GENERATED_PROJECT_DOWNLOAD_CONFIGS", []):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, sample)
            with patch(
                "scpca_portal.common.PRE_GENERATED_SAMPLE_DOWNLOAD_CONFIGS", [download_config]
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_download_config_file_output_name(download_config)
        sample_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999991"}
            self.assertCorrectLibraries(sample_zip, expected_libraries)

            expected_file_list = [
                "README.md",
                "spatial_metadata.tsv",
                "SCPCL999991_spatial/SCPCL999991_spaceranger-summary.html",
                "SCPCL999991_spatial/filtered_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCL999991_spatial/filtered_feature_bc_matrix/features.tsv.gz",
                "SCPCL999991_spatial/filtered_feature_bc_matrix/matrix.mtx.gz",
                "SCPCL999991_spatial/raw_feature_bc_matrix/barcodes.tsv.gz",
                "SCPCL999991_spatial/raw_feature_bc_matrix/features.tsv.gz",
                "SCPCL999991_spatial/raw_feature_bc_matrix/matrix.mtx.gz",
                "SCPCL999991_spatial/spatial/aligned_fiducials.jpg",
                "SCPCL999991_spatial/spatial/detected_tissue_image.jpg",
                "SCPCL999991_spatial/spatial/scalefactors_json.json",
                "SCPCL999991_spatial/spatial/tissue_hires_image.png",
                "SCPCL999991_spatial/spatial/tissue_lowres_image.png",
                "SCPCL999991_spatial/spatial/tissue_positions_list.csv",
                "SCPCL999991_spatial/SCPCL999991_metadata.json",
            ]
            result_file_list = sample_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()
        self.assertIsNotNone(computed_file)

        expected_computed_file_attribute_values = {
            "format": ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            "has_bulk_rna_seq": False,
            "has_cite_seq_data": False,
            "has_multiplexed_data": False,
            "includes_merged": False,
            "modality": ComputedFile.OutputFileModalities.SPATIAL,
            "metadata_only": False,
            "s3_bucket": settings.AWS_S3_OUTPUT_BUCKET_NAME,
            "s3_key": output_file_name,
            "size_in_bytes": 8820,
            "workflow_version": "development",
            "includes_celltype_report": True,
        }
        self.assertObjectProperties(computed_file, expected_computed_file_attribute_values)
