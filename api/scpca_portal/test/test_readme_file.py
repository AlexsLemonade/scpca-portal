from django.test import TestCase

from scpca_portal import utils


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
