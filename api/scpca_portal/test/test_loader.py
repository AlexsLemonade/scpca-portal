import io
from csv import DictReader
from functools import partial
from pathlib import Path
from typing import Any, Dict, Set
from zipfile import ZipFile

from django.conf import settings
from django.test import TransactionTestCase

from scpca_portal import common, loader, metadata_file
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
                self.assertEqual(set(getattr(obj, attribute)), set(value), msg)
            else:
                self.assertEqual(getattr(obj, attribute), value, msg)

    def assertDictIsNonEmpty(self, d: Dict) -> None:
        self.assertTrue(any(key for key in d))

    def get_computed_files_query_params_from_download_config(self, download_config: Dict) -> Dict:
        if download_config["metadata_only"]:
            return {"metadata_only": download_config["metadata_only"]}

        query_params = {
            "modality": download_config["modality"],
            "format": download_config["format"],
        }

        if download_config in common.GENERATED_SAMPLE_DOWNLOAD_CONFIGURATIONS.values():
            return query_params

        query_params["has_multiplexed_data"] = not download_config["excludes_multiplexed"]
        query_params["includes_merged"] = download_config["includes_merged"]

        return query_params

    def assertCorrectLibraries(self, project_zip: ZipFile, expected_libraries: Set[str]) -> None:
        file_list = project_zip.namelist()

        # Check via metadata file
        metadata_file_name = next(file_name for file_name in file_list if "metadata" in file_name)
        metadata_file = project_zip.read(metadata_file_name)
        metadata_file_str = io.StringIO(metadata_file.decode("utf-8"))
        metadata_file_dict_reader = DictReader(metadata_file_str, delimiter="\t")

        metadata_file_libraries = set(row["scpca_library_id"] for row in metadata_file_dict_reader)
        self.assertEqual(expected_libraries, metadata_file_libraries)

        # Check via data file paths
        data_file_libraries = set(
            # data files have paths that look like "SCPCS999990/SCPCL999990_processed.rds"
            Path(file).name.split("_")[0]
            for file in file_list
            # all data files have parents, non parent files include the metadata and readme files
            if "/" in file
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
        expected_project_attributes_values = {
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
        self.assertObjectProperties(project, expected_project_attributes_values)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 4)

        # SCPCS999990
        sample_id = "SCPCS999990"
        sample = project.samples.filter(scpca_id=sample_id).first()

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

        expected_summary_attribute_values = {
            "diagnosis": "diagnosis1",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        expected_summary_attribute_values = {
            "diagnosis": "diagnosis2",
            "sample_count": 1,
            "seq_unit": "spot",
            "technology": "visium",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        expected_summary_attribute_values = {
            "diagnosis": "diagnosis5",
            "sample_count": 1,
            "seq_unit": "",
            "technology": "",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        expected_summary_attribute_values = {
            "diagnosis": "diagnosis8",
            "sample_count": 1,
            "seq_unit": "cell",
            "technology": "10Xv3",
        }
        self.assertTrue(project.summaries.filter(**expected_summary_attribute_values).exists())

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        email = "{email contact 1}"
        contact = project.contacts.filter(email=email).first()
        expected_contact_attribute_values = {
            "name": "{contact 1}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        email = "{email contact 2}"
        contact = project.contacts.filter(email=email).first()
        expected_contact_attribute_values = {
            "name": "{contact 2}",
            "email": email,
            "pi_name": "scpca",
        }
        self.assertObjectProperties(contact, expected_contact_attribute_values)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        accession = "{SRA project accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
        expected_external_accession_attribute_values = {
            "accession": accession,
            "has_raw": True,
            "url": "{SRA Run Selector URL}",
        }
        self.assertObjectProperties(
            external_accession, expected_external_accession_attribute_values
        )

        accession = "{GEO series accession}"
        external_accession = project.external_accessions.filter(accession=accession).first()
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

        doi = "{doi 1}"
        publication = project.publications.filter(doi=doi).first()
        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 1}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

        doi = "{doi 2}"
        publication = project.publications.filter(doi=doi).first()
        expected_publication_attribute_values = {
            "doi": doi,
            "citation": "{formatted citation 2}",
            "pi_name": "scpca",
        }
        self.assertObjectProperties(publication, expected_publication_attribute_values)

    def test_create_project_SCPCP999991(self):
        pass

    def test_create_project_SCPCP999992(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        loader.prep_data_dirs()

        project_id = "SCPCP999990"
        project = self.create_project(self.get_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(project)

        self.generate_computed_files(project)

        download_config = common.GENERATED_PROJECT_DOWNLOAD_CONFIGURATIONS[
            "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        ]
        output_file_name = project.get_download_config_file_output_name(download_config)
        project_zip_path = common.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Basic Metadata file check
            sample_metadata = project_zip.read(
                metadata_file.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME
            )
            sample_metadata_lines = [
                sm for sm in sample_metadata.decode("utf-8").split("\r\n") if sm
            ]
            self.assertEqual(len(sample_metadata_lines), 3)  # 2 items + header.

            # Basic Readme check
            self.assertProjectReadmeContains(
                "This dataset is designated as research or academic purposes only.",
                project_zip,
            )

            # Check if correct libraries were added in
            expected_libraries = {"SCPCL999990", "SCPCL999997"}
            self.assertCorrectLibraries(project_zip, expected_libraries)

            # Check that correct files were added in
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
                "SCPCP999990_bulk_metadata.tsv",
                "SCPCP999990_bulk_quant.tsv",
                "single_cell_metadata.tsv",
            ]
            result_file_list = project_zip.namelist()
            self.assertEqual(set(expected_file_list), set(result_file_list))

        # Check computed file attributes
        computed_file = project.computed_files.filter(
            **self.get_computed_files_query_params_from_download_config(download_config)
        ).first()

        self.assertEqual(
            computed_file.format, ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT
        )
        self.assertFalse(computed_file.includes_merged)
        self.assertFalse(computed_file.metadata_only)
        self.assertEqual(computed_file.s3_bucket, settings.AWS_S3_OUTPUT_BUCKET_NAME)
        self.assertEqual(computed_file.s3_key, output_file_name)
        self.assertEqual(computed_file.size_in_bytes, 9078)
        self.assertEqual(computed_file.workflow_version, "development")
        self.assertTrue(computed_file.includes_celltype_report)
        self.assertTrue(computed_file.has_bulk_rna_seq)
        self.assertFalse(computed_file.has_cite_seq_data)
        self.assertFalse(computed_file.has_multiplexed_data)

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA_MERGED(self):
        pass

    def test_project_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_project_generate_computed_files_ALL_METADATA(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        pass

    def test_sample_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        pass

    def test_sample_generate_computed_files_SPATIAL_SINGLE_CELL_EXPERIMENT(self):
        pass