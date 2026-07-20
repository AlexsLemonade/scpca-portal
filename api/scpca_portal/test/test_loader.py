import io
from csv import DictReader
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Set
from zipfile import ZipFile

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from scpca_portal import loader, metadata_parser, utils
from scpca_portal.models import Project
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
