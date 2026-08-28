from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from scpca_portal import loader, metadata_parser, utils
from scpca_portal.enums import CCDLDatasetNames
from scpca_portal.models import CCDLDataset
from scpca_portal.readme_file import get_file_contents_dataset
from scpca_portal.test import expected_values as test_data

README_ROOT = settings.RENDERED_README_PATH


# This is a regression test to ensure README output remains correct for all CCDL name variants.
class TestReadmeFileContents(TestCase):
    def assertReadmeContents(self, expected_file_path: str, result_content: str) -> None:
        with open(expected_file_path, encoding="utf-8") as expected_file:
            # Replace the placeholder TEST_TODAYS_DATE in expected_values/readmes with today's date
            expected_content = (
                expected_file.read().replace("TEST_TODAYS_DATE", utils.get_today_string()).strip()
            )
        # Convert expected and result contents to line lists for easier debugging
        self.assertEqual(
            expected_content.splitlines(True),
            result_content.splitlines(True),
            f"{self._testMethodName}: Comparison with {expected_file_path} does not match.",
        )

    @classmethod
    def setUpTestData(cls):
        bucket = settings.AWS_S3_INPUT_BUCKET_NAME
        call_command("sync_original_files", bucket=bucket)

        loader.download_projects_metadata()
        project_ids = metadata_parser.get_projects_metadata_ids(bucket=bucket)

        loader.download_projects_related_metadata(project_ids)
        for project_metadata in metadata_parser.load_projects_metadata(project_ids):
            loader.create_project(
                project_metadata,
                submitter_whitelist={"scpca"},
                input_bucket_name=bucket,
                reload_existing=True,
                update_s3=False,
            )

    def test_readme_file_ALL_METADATA(self):
        expected_file_path = README_ROOT / f"{CCDLDatasetNames.ALL_METADATA}.md"
        expected_values = test_data.CCDLDatasetAllMetadata

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        # Dataset containing the project with no multiplexed samples
        expected_file_path = (
            README_ROOT / f"{CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT}.md"
        )
        expected_values = test_data.CCDLDatasetSingleCellSingleCellExperimentMergedSCPCP999990

        dataset, _ = CCDLDataset.get_or_find(
            expected_values.CCDL_NAME, project_id=expected_values.PROJECT_ID
        )
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        # This test uses a one-off, non-CCDLDatasetNames README filename to test
        # a dataset with multiplexed samples
        #
        # NOTE: Dataset containing the project with multiplexed samples maps to
        # CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT in production
        expected_file_path = README_ROOT / "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED.md"
        expected_values = test_data.CCDLDatasetSingleCellSingleCellExperiment

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED(self):
        # Dataset containing the project excluding multiplexed samples
        expected_file_path = (
            README_ROOT / f"{CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED}.md"
        )
        expected_values = (
            test_data.CCDLDatasetSingleCellSingleCellExperimentNoMultiplexedSCPCP999991
        )

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME, expected_values.PROJECT_ID)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        expected_file_path = (
            README_ROOT / f"{CCDLDatasetNames.SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED}.md"
        )
        expected_values = test_data.CCDLDatasetSingleCellSingleCellExperimentMerged

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_ANN_DATA(self):
        expected_file_path = README_ROOT / f"{CCDLDatasetNames.SINGLE_CELL_ANN_DATA}.md"
        expected_values = test_data.CCDLDatasetSingleCellAnndata

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SINGLE_CELL_ANN_DATA_MERGED(self):
        expected_file_path = README_ROOT / f"{CCDLDatasetNames.SINGLE_CELL_ANN_DATA_MERGED}.md"
        expected_values = test_data.CCDLDatasetSingleCellAnndataMerged

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )

    def test_readme_file_SPATIAL_SPATIAL_SPACERANGER(self):
        expected_file_path = README_ROOT / f"{CCDLDatasetNames.SPATIAL_SPATIAL_SPACERANGER}.md"
        expected_values = test_data.CCDLDatasetSpatialSpatialSpaceranger

        dataset, _ = CCDLDataset.get_or_find(expected_values.CCDL_NAME)
        dataset.save()

        result_content = get_file_contents_dataset(dataset)

        self.assertReadmeContents(
            expected_file_path,
            result_content,
        )
