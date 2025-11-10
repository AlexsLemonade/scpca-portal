from django.conf import settings
from django.test import TestCase

from scpca_portal import common, readme_file, utils
from scpca_portal.test.factories import ProjectFactory


class TestReadmeFileContents(TestCase):
    def assertReadmeContents(self, expected_file_path: str, result_content: str) -> None:
        with open(expected_file_path, encoding="utf-8") as expected_file:
            # Replace the placeholder TEST_TODAYS_DATE in expected_values/readmes with today
            expected_content = (
                expected_file.read()
                .replace(
                    "Generated on: TEST_TODAYS_DATE", f"Generated on: {utils.get_today_string()}"
                )
                .strip()
            )
        # Convert expected and result contents to line lists for easier debugging
        self.assertEqual(
            expected_content.splitlines(True),
            result_content.splitlines(True),
            f"{self._testMethodName}: Comparison with {expected_file_path} does not match.",
        )

    def test_readme_file_PORTAL_ALL_METADATA(self):
        DOWNLOAD_CONFIG_NAME = "PORTAL_ALL_METADATA"
        DOWNLOAD_CONFIG = common.PORTAL_METADATA_DOWNLOAD_CONFIG
        PROJECT_IDS = ["PROJECT_ID_0", "PROJECT_ID_1", "PROJECT_ID_2"]

        projects = [ProjectFactory(scpca_id=project_id) for project_id in PROJECT_IDS]
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, projects)
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_ALL_METADATA(self):
        DOWNLOAD_CONFIG_NAME = "ALL_METADATA"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT(self):
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED(self):
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MULTIPLEXED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED(self):
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SINGLE_CELL_ANN_DATA(self):
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_ANN_DATA"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SINGLE_CELL_ANN_DATA_MERGED(self):
        DOWNLOAD_CONFIG_NAME = "SINGLE_CELL_ANN_DATA_MERGED"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)

    def test_readme_file_SPATIAL(self):
        DOWNLOAD_CONFIG_NAME = "SPATIAL_SINGLE_CELL_EXPERIMENT"
        DOWNLOAD_CONFIG = common.PROJECT_DOWNLOAD_CONFIGS[DOWNLOAD_CONFIG_NAME]
        PROJECT_ID = "PROJECT_ID_0"

        project = ProjectFactory(scpca_id=PROJECT_ID)
        result = readme_file.get_file_contents(DOWNLOAD_CONFIG, [project])
        expected_file_path = settings.RENDERED_README_PATH / f"{DOWNLOAD_CONFIG_NAME}.md"
        self.assertReadmeContents(expected_file_path, result)
