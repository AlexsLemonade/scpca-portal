import io
from csv import DictReader
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Set
from unittest.mock import patch
from zipfile import ZipFile

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import loader, metadata_parser, utils
from scpca_portal.models import ComputedFile, Project
from scpca_portal.test import expected_values as test_data


class TestLoader(TransactionTestCase):
    def setUp(self):
        call_command("sync_original_files", bucket=settings.AWS_S3_INPUT_BUCKET_NAME)

        # When passing a project_id to load_projects_metadata, a list of one item is returned
        # This lambda creates a shorthand to access the single returned project_metadata
        def load_project_metadata(project_id):
            loader.download_projects_metadata()
            loader.download_projects_related_metadata([project_id])
            return metadata_parser.load_projects_metadata([project_id])[0]

        self.load_project_metadata = load_project_metadata

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

    def purge_extra_samples(self, project: Project, samples_of_interest: List[str]) -> None:
        """Purges all of a project's samples that are not the samples of interest."""
        for sample in project.samples.all():
            if sample.scpca_id not in samples_of_interest:
                sample.purge()

    def assertObjectProperties(self, obj: Any, expected_values: Dict[str, Any]) -> None:
        for attribute, value in expected_values.items():
            msg = f"The actual and expected `{attribute}` values differ in {obj}"
            if isinstance(value, list):
                self.assertListEqual(getattr(obj, attribute), value, msg)
            else:
                self.assertEqual(getattr(obj, attribute), value, msg)

    def assertDictIsNonEmpty(self, d: Dict) -> None:
        self.assertTrue(any(key for key in d))

    def assertLibraries(self, project_zip: ZipFile, expected_libraries: Set[str]) -> None:
        self.assertLibrariesMetadata(project_zip, expected_libraries)
        self.assertLibrariesOriginalFiles(project_zip, expected_libraries)

    def assertLibrariesMetadata(self, project_zip: ZipFile, expected_libraries: Set[str]) -> None:
        file_list = project_zip.namelist()

        # Check via metadata file
        metadata_file_name = next(file_name for file_name in file_list if "metadata" in file_name)
        metadata_file = project_zip.read(metadata_file_name)

        with io.StringIO(metadata_file.decode("utf-8")) as metadata_file_str:
            metadata_file_dict_reader = DictReader(metadata_file_str, delimiter="\t")
            metadata_file_libraries = set(
                row["scpca_library_id"] for row in metadata_file_dict_reader
            )
            self.assertEqual(metadata_file_libraries, expected_libraries)

    def assertLibrariesOriginalFiles(
        self, project_zip: ZipFile, expected_libraries: Set[str]
    ) -> None:
        original_file_paths = [Path(file) for file in project_zip.namelist()]
        original_file_libraries = set(
            # data files have paths that look like "SCPCS999990/SCPCL999990_processed.rds"
            file_path.name.split("_")[0]
            for file_path in original_file_paths
            if file_path.name.startswith("SCPCL")
        )
        self.assertEqual(original_file_libraries, expected_libraries)

    def test_create_project_SCPCP999990(self):
        utils.create_data_dirs()

        returned_project = self.create_project(
            self.load_project_metadata(test_data.Project_SCPCP999990.SCPCA_ID)
        )

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=test_data.Project_SCPCP999990.SCPCA_ID).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        self.assertObjectProperties(project, test_data.Project_SCPCP999990.VALUES)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 4)

        # SCPCS999990
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999990.Sample_SCPCS999990.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999990.Sample_SCPCS999990.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999991
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999990.Sample_SCPCS999991.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999990.Sample_SCPCS999991.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999994
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999990.Sample_SCPCS999994.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999990.Sample_SCPCS999994.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999997
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999990.Sample_SCPCS999997.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999990.Sample_SCPCS999997.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 4)

        # SCPCL999990
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999990.Library_SCPCL999990.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999990.Library_SCPCL999990.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999991
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999990.Library_SCPCL999991.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999990.Library_SCPCL999991.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999994
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999990.Library_SCPCL999994.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999990.Library_SCPCL999994.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999997
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999990.Library_SCPCL999997.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999990.Library_SCPCL999997.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 3)

        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999990.Summary1.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999990.Summary1.VALUES}",
        )
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999990.Summary2.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999990.Summary2.VALUES}",
        )
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999990.Summary4.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999990.Summary4.VALUES}",
        )

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999990.Contact1.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999990.Contact1.VALUES)

        # Second contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999990.Contact2.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999990.Contact2.VALUES)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999990.ExternalAccession1.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999990.ExternalAccession1.VALUES
        )

        # Second external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999990.ExternalAccession2.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999990.ExternalAccession2.VALUES
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999990.Publication1.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999990.Publication1.VALUES)

        # Second publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999990.Publication2.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999990.Publication2.VALUES)

    def test_create_project_SCPCP999991(self):
        utils.create_data_dirs()

        returned_project = self.create_project(
            self.load_project_metadata(test_data.Project_SCPCP999991.SCPCA_ID)
        )

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=test_data.Project_SCPCP999991.SCPCA_ID).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        self.assertObjectProperties(project, test_data.Project_SCPCP999991.VALUES)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 3)

        # SCPCS999992
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999991.Sample_SCPCS999992.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999991.Sample_SCPCS999992.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999993
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999991.Sample_SCPCS999993.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999991.Sample_SCPCS999993.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999995
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999991.Sample_SCPCS999995.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999991.Sample_SCPCS999995.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 2)

        # SCPCL999992
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999991.Library_SCPCL999992.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999991.Library_SCPCL999992.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999995
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999991.Library_SCPCL999995.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999991.Library_SCPCL999995.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 3)
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999991.Summary1.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999991.Summary1.VALUES}",
        )
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999991.Summary2.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999991.Summary2.VALUES}",
        )
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999991.Summary3.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999991.Summary3.VALUES}",
        )

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999991.Contact1.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999991.Contact1.VALUES)

        # Second contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999991.Contact2.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999991.Contact2.VALUES)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999991.ExternalAccession1.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999991.ExternalAccession1.VALUES
        )

        # Second external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999991.ExternalAccession2.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999991.ExternalAccession2.VALUES
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999991.Publication1.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999991.Publication1.VALUES)

        # Second publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999991.Publication2.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999991.Publication2.VALUES)

    def test_create_project_SCPCP999992(self):
        utils.create_data_dirs()

        returned_project = self.create_project(
            self.load_project_metadata(test_data.Project_SCPCP999992.SCPCA_ID)
        )

        # CHECK FOR PROJECT EXISTENCE
        project = Project.objects.filter(scpca_id=test_data.Project_SCPCP999992.SCPCA_ID).first()
        self.assertEqual(project, returned_project)

        # CHECK PROJECT ATTRIBUTE VALUES
        self.assertObjectProperties(project, test_data.Project_SCPCP999992.VALUES)

        # CHECK SAMPLE VALUES
        self.assertEqual(project.samples.count(), 2)

        # SCPCS999996
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999992.Sample_SCPCS999996.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999992.Sample_SCPCS999996.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # SCPCS999998
        sample = project.samples.filter(
            scpca_id=test_data.Project_SCPCP999992.Sample_SCPCS999998.SCPCA_ID
        ).first()
        self.assertIsNotNone(sample)
        self.assertObjectProperties(sample, test_data.Project_SCPCP999992.Sample_SCPCS999998.VALUES)
        self.assertDictIsNonEmpty(sample.metadata)

        # CHECK LIBRARY VALUES
        self.assertEqual(project.libraries.count(), 2)

        # SCPCL999996
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999992.Library_SCPCL999996.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999992.Library_SCPCL999996.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # SCPCL999998
        library = project.libraries.filter(
            scpca_id=test_data.Project_SCPCP999992.Library_SCPCL999998.SCPCA_ID
        ).first()
        self.assertIsNotNone(library)
        self.assertObjectProperties(
            library, test_data.Project_SCPCP999992.Library_SCPCL999998.VALUES
        )
        # Assert that metadata attribute has been populated and did not default to empty dict
        self.assertDictIsNonEmpty(library.metadata)

        # CHECK PROJECT SUMMARIES VALUES
        self.assertEqual(project.summaries.count(), 2)
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999992.Summary1.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999992.Summary1.VALUES}",
        )
        self.assertTrue(
            project.summaries.filter(**test_data.Project_SCPCP999992.Summary2.VALUES).exists(),
            f"No Project Summary exists for {project.scpca_id} which matches the following values: "
            f"{test_data.Project_SCPCP999992.Summary2.VALUES}",
        )

        # CHECK CONTACTS
        self.assertEqual(project.contacts.count(), 2)

        # First contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999992.Contact1.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999992.Contact1.VALUES)

        # Second contact
        contact = project.contacts.filter(
            email=test_data.Project_SCPCP999992.Contact2.EMAIL
        ).first()
        self.assertIsNotNone(contact)
        self.assertObjectProperties(contact, test_data.Project_SCPCP999992.Contact2.VALUES)

        # CHECK EXTERNAL ACCESSION VALUES
        self.assertEqual(project.external_accessions.count(), 2)

        # First external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999992.ExternalAccession1.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999992.ExternalAccession1.VALUES
        )

        # Second external accession
        external_accession = project.external_accessions.filter(
            accession=test_data.Project_SCPCP999992.ExternalAccession2.ACCESSION
        ).first()
        self.assertIsNotNone(external_accession)
        self.assertObjectProperties(
            external_accession, test_data.Project_SCPCP999992.ExternalAccession2.VALUES
        )

        # CHECK PUBLICATIONS VALUES
        self.assertEqual(project.publications.count(), 2)

        # First publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999992.Publication1.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999992.Publication1.VALUES)

        # Second publication
        publication = project.publications.filter(
            doi=test_data.Project_SCPCP999992.Publication2.DOI
        ).first()
        self.assertIsNotNone(publication)
        self.assertObjectProperties(publication, test_data.Project_SCPCP999992.Publication2.VALUES)

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(test_data.Computed_File_Project.SINGLE_CELL_SCE.PROJECT_ID)
        )
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = test_data.Computed_File_Project.SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME
        download_config = test_data.Computed_File_Project.SINGLE_CELL_SCE.DOWNLOAD_CONFIG
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = test_data.Computed_File_Project.SINGLE_CELL_SCE.LIBRARIES
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SINGLE_CELL_SCE.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SINGLE_CELL_SCE.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.SINGLE_CELL_SCE.VALUES
        )

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(
                test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.PROJECT_ID
            )
        )
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = (
            test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.DOWNLOAD_CONFIG_NAME
        )
        download_config = (
            test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.DOWNLOAD_CONFIG
        )
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = (
                test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.LIBRARIES
            )
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.SINGLE_CELL_SCE_MULTIPLEXED.VALUES
        )

    def test_project_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(
                test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.PROJECT_ID
            )
        )
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = (
            test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.DOWNLOAD_CONFIG_NAME
        )
        download_config = test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.DOWNLOAD_CONFIG
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.LIBRARIES
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.SINGLE_CELL_SCE_MERGED.VALUES
        )

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(
                test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.PROJECT_ID
            )
        )
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = (
            test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG_NAME
        )
        download_config = test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.LIBRARIES
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA.VALUES
        )

    def test_project_generate_computed_files_SINGLE_CELL_ANN_DATA_MERGED(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(
                test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.PROJECT_ID
            )
        )
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = (
            test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.DOWNLOAD_CONFIG_NAME
        )
        download_config = (
            test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.DOWNLOAD_CONFIG
        )
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = (
                test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.LIBRARIES
            )
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.SINGLE_CELL_ANN_DATA_MERGED.VALUES
        )

    def test_project_generate_computed_files_SPATIAL(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project = self.create_project(
            self.load_project_metadata(test_data.Computed_File_Project.SPATIAL.PROJECT_ID)
        )
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.SPATIAL.DOWNLOAD_CONFIG_NAME}",  # noqa
        )

        download_config_name = test_data.Computed_File_Project.SPATIAL.DOWNLOAD_CONFIG_NAME
        download_config = test_data.Computed_File_Project.SPATIAL.DOWNLOAD_CONFIG
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {download_config_name: download_config}
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = test_data.Computed_File_Project.SPATIAL.LIBRARIES
            self.assertLibraries(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.SPATIAL.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.SPATIAL.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(computed_file, test_data.Computed_File_Project.SPATIAL.VALUES)

    def test_project_generate_computed_files_ALL_METADATA(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = test_data.Computed_File_Project.ALL_METADATA.PROJECT_ID
        project = self.create_project(self.load_project_metadata(project_id))
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_project_generate_computed_file_"
            f"{test_data.Computed_File_Project.ALL_METADATA.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = test_data.Computed_File_Project.ALL_METADATA.DOWNLOAD_CONFIG_NAME
        download_config = test_data.Computed_File_Project.ALL_METADATA.DOWNLOAD_CONFIG
        with patch(
            "scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS",
            {download_config_name: download_config},
        ):
            with patch("scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS", {}):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = project.get_output_file_name(download_config)
        project_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(project_zip_path) as project_zip:
            # Check if correct libraries were added in
            expected_libraries = test_data.Computed_File_Project.ALL_METADATA.LIBRARIES
            # assertLibrariesMetadata and not assertLibrariesOriginalFiles for ALL_METADATA config
            self.assertLibrariesMetadata(project_zip, expected_libraries)
            # Check if file list is as expected
            self.assertListEqual(
                sorted(project_zip.namelist()),
                test_data.Computed_File_Project.ALL_METADATA.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = project.get_computed_file(
            test_data.Computed_File_Project.ALL_METADATA.DOWNLOAD_CONFIG
        )
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Project.ALL_METADATA.VALUES
        )

    def test_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = test_data.Computed_File_Sample.SINGLE_CELL_SCE.PROJECT_ID
        project = self.create_project(self.load_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME}",
        )

        sample_id = test_data.Computed_File_Sample.SINGLE_CELL_SCE.SAMPLE_ID
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(
            sample,
            "Problem retrieving sample, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = test_data.Computed_File_Sample.SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME
        download_config = test_data.Computed_File_Sample.SINGLE_CELL_SCE.DOWNLOAD_CONFIG
        with patch("scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {}):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, [sample_id])
            with patch(
                "scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS",
                {download_config_name: download_config},
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_output_file_name(download_config)
        sample_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            self.assertLibraries(
                sample_zip, test_data.Computed_File_Sample.SINGLE_CELL_SCE.LIBRARIES
            )
            self.assertListEqual(
                sorted(sample_zip.namelist()),
                test_data.Computed_File_Sample.SINGLE_CELL_SCE.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.get_computed_file(download_config)
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Sample.SINGLE_CELL_SCE.VALUES
        )

    def test_sample_generate_computed_files_SINGLE_CELL_ANN_DATA(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.PROJECT_ID
        project = self.create_project(self.load_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG_NAME}",
        )

        sample_id = test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.SAMPLE_ID
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(
            sample,
            "Problem retrieving sample, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = (
            test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG_NAME
        )
        download_config = test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.DOWNLOAD_CONFIG
        with patch("scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {}):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, [sample_id])
            with patch(
                "scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS",
                {download_config_name: download_config},
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_output_file_name(download_config)
        sample_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            self.assertLibraries(
                sample_zip, test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.LIBRARIES
            )
            self.assertListEqual(
                sorted(sample_zip.namelist()),
                test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.get_computed_file(download_config)
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(
            computed_file, test_data.Computed_File_Sample.SINGLE_CELL_ANN_DATA.VALUES
        )

    def test_sample_generate_computed_files_SPATIAL(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = test_data.Computed_File_Sample.SPATIAL.PROJECT_ID
        project = self.create_project(self.load_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SPATIAL.DOWNLOAD_CONFIG_NAME}",
        )

        sample_id = test_data.Computed_File_Sample.SPATIAL.SAMPLE_ID
        sample = project.samples.filter(scpca_id=sample_id).first()
        self.assertIsNotNone(
            sample,
            "Problem retrieving sample, unable to test "
            "test_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.SPATIAL.DOWNLOAD_CONFIG_NAME}",
        )

        download_config_name = test_data.Computed_File_Sample.SPATIAL.DOWNLOAD_CONFIG_NAME
        download_config = test_data.Computed_File_Sample.SPATIAL.DOWNLOAD_CONFIG
        with patch("scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {}):
            # Mocking project.samples.all() in loader module is restricted due to the Django ORM
            # Instead, we purge all samples that are not of interest to desired computed file
            self.purge_extra_samples(project, [sample_id])
            with patch(
                "scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS",
                {download_config_name: download_config},
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_output_file_name(download_config)
        sample_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            self.assertLibraries(sample_zip, test_data.Computed_File_Sample.SPATIAL.LIBRARIES)
            self.assertListEqual(
                sorted(sample_zip.namelist()),
                test_data.Computed_File_Sample.SPATIAL.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        computed_file = sample.get_computed_file(download_config)
        self.assertIsNotNone(computed_file)
        self.assertObjectProperties(computed_file, test_data.Computed_File_Sample.SPATIAL.VALUES)

    def test_multiplexed_sample_generate_computed_files_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        utils.create_data_dirs()

        # GENERATE COMPUTED FILES
        project_id = test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.PROJECT_ID
        project = self.create_project(self.load_project_metadata(project_id))
        # Make sure that create_project didn't fail and return a None value
        self.assertIsNotNone(
            project,
            "Problem creating project, unable to test "
            "test_multiplexed_sample_generate_computed_file_"
            f"{test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME}",
        )

        sample_ids = test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.SAMPLE_IDS
        for sample_id in sample_ids:
            sample = project.samples.filter(scpca_id=sample_id).first()
            self.assertIsNotNone(
                sample,
                f"Problem retrieving {sample_id}, unable to test "
                "test_multiplexed_sample_generate_computed_file_"
                f"{test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME}",  # noqa
            )

        download_config_name = (
            test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.DOWNLOAD_CONFIG_NAME
        )
        download_config = test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.DOWNLOAD_CONFIG

        with patch("scpca_portal.common.PROJECT_DOWNLOAD_CONFIGS", {}):
            # While only one sample of intended modality and format is necessary for other tests,
            # all multiplexed samples must be present to validate correctness here.
            # This is a result of how we create multiplexed sample computed files,
            # where we take the sample with the highest id for computed file generation,
            # and build computed file objects for other samples from the chosen sample.
            self.purge_extra_samples(project, sample_ids)
            with patch(
                "scpca_portal.common.SAMPLE_DOWNLOAD_CONFIGS",
                {download_config_name: download_config},
            ):
                self.generate_computed_files(project)

        # CHECK ZIP FILE
        output_file_name = sample.get_output_file_name(download_config)
        sample_zip_path = settings.OUTPUT_DATA_PATH / output_file_name
        with ZipFile(sample_zip_path) as sample_zip:
            # Check if correct libraries were added in
            self.assertLibraries(
                sample_zip, test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.LIBRARIES
            )
            self.assertListEqual(
                sorted(sample_zip.namelist()),
                test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.FILE_LIST,
            )

        # CHECK COMPUTED FILE ATTRIBUTES
        self.assertEqual(len(sample_ids), ComputedFile.objects.count())
        for sample_id in sample_ids:
            sample = project.samples.filter(scpca_id=sample_id).first()
            computed_file = sample.get_computed_file(download_config)
            self.assertIsNotNone(computed_file)
            # Check for identical computed files amongst multiplexed samples
            self.assertObjectProperties(
                computed_file, test_data.Computed_File_Sample.MULTIPLEXED_SINGLE_CELL_SCE.VALUES
            )
