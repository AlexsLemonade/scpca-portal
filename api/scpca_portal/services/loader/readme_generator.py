
from django.template.loader import render_to_string

from scpca_portal import common, utils
from scpca_portal.models import ComputedFile


class ReadMeGenerator():
    # Create readmes for all four possible scenarios.
    # The one that corresponds to the current project will be renamed "README.md" and outputted
    OUTPUT_README_FILE_NAME = "README.md"

    README_ANNDATA_FILE_NAME = "readme_anndata.md"
    README_ANNDATA_FILE_PATH = common.OUTPUT_DATA_PATH / README_ANNDATA_FILE_NAME

    README_SINGLE_CELL_FILE_NAME = "readme_single_cell.md"
    README_SINGLE_CELL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SINGLE_CELL_FILE_NAME

    README_MULTIPLEXED_FILE_NAME = "readme_multiplexed.md"
    README_MULTIPLEXED_FILE_PATH = common.OUTPUT_DATA_PATH / README_MULTIPLEXED_FILE_NAME

    README_SPATIAL_FILE_NAME = "readme_spatial.md"
    README_SPATIAL_FILE_PATH = common.OUTPUT_DATA_PATH / README_SPATIAL_FILE_NAME

    README_TEMPLATE_PATH = common.TEMPLATE_PATH / "readme"
    README_TEMPLATE_ANNDATA_FILE_PATH = README_TEMPLATE_PATH / "anndata.md"
    README_TEMPLATE_SINGLE_CELL_FILE_PATH = README_TEMPLATE_PATH / "single_cell.md"
    README_TEMPLATE_MULTIPLEXED_FILE_PATH = README_TEMPLATE_PATH / "multiplexed.md"
    README_TEMPLATE_SPATIAL_FILE_PATH = README_TEMPLATE_PATH / "spatial.md"

    def create_readmes(self, scpca_project_id: str) -> None:
        self.scpca_project_id = scpca_project_id

        self.create_anndata_readme_file()
        self.create_multiplexed_readme_file()
        self.create_single_cell_readme_file()
        self.create_spatial_readme_file()

    def create_anndata_readme_file(self, scpca_id):
        """Creates a annotation metadata README file."""
        with open(ComputedFile.README_ANNDATA_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_ANNDATA_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_project_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_multiplexed_readme_file(self, scpca_id):
        """Creates a multiplexed metadata README file."""
        with open(ComputedFile.README_MULTIPLEXED_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_MULTIPLEXED_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_project_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_single_cell_readme_file(self, scpca_id):
        """Creates a single cell metadata README file."""
        with open(ComputedFile.README_SINGLE_CELL_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_SINGLE_CELL_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_project_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def create_spatial_readme_file(self, scpca_id):
        """Creates a spatial metadata README file."""
        with open(ComputedFile.README_SPATIAL_FILE_PATH, "w") as readme_file:
            readme_file.write(
                render_to_string(
                    ComputedFile.README_TEMPLATE_SPATIAL_FILE_PATH,
                    context={
                        "additional_terms": self.get_additional_terms(),
                        "date": utils.get_today_string(),
                        "project_accession": self.scpca_id,
                        "project_url": self.url,
                    },
                ).strip()
            )

    def get_additional_terms(self):
        if not self.additional_restrictions:
            return ""

        with open(
            common.TEMPLATE_PATH / "readme/additional_terms/research_academic_only.md"
        ) as additional_terms_file:
            return additional_terms_file.read()

    @property
    def url(self):
        return f"https://scpca.alexslemonade.org/projects/{self.scpca_id}"
