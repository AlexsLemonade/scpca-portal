from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.db import models

from scpca_portal import common, metadata_parser
from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.models.base import TimestampedModel
from scpca_portal.models.original_file import OriginalFile


class Library(TimestampedModel):
    class Meta:
        db_table = "libraries"
        get_latest_by = "updated_at"
        ordering = ["updated_at"]

    formats = ArrayField(models.TextField(choices=FileFormats.choices), default=list)
    has_cite_seq_data = models.BooleanField(default=False)
    is_multiplexed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    modality = models.TextField(choices=Modalities.choices)
    scpca_id = models.TextField(unique=True)
    workflow_version = models.TextField()

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="libraries")

    def __str__(self):
        return f"Library {self.scpca_id}"

    @classmethod
    def get_from_dict(cls, data, project):
        library_id = data["scpca_library_id"]
        original_files = OriginalFile.downloadable_objects.filter(library_id=library_id)

        modality = ""
        if original_files.filter(is_single_cell=True).exists():
            modality = Modalities.SINGLE_CELL
        elif original_files.filter(is_spatial=True).exists():
            modality = Modalities.SPATIAL
        elif data.get("seq_unit") == "bulk":
            modality = Modalities.BULK_RNA_SEQ

        formats = []
        if modality == Modalities.SPATIAL:
            if original_files.filter(is_spatial_spaceranger=True).exists():
                formats.append(FileFormats.SPATIAL_SPACERANGER)
        else:
            if original_files.filter(is_single_cell_experiment=True).exists():
                formats.append(FileFormats.SINGLE_CELL_EXPERIMENT)
            if original_files.filter(is_anndata=True).exists():
                formats.append(FileFormats.ANN_DATA)

        library = cls(
            formats=sorted(formats),
            is_multiplexed=data.get("is_multiplexed", False),
            has_cite_seq_data=original_files.filter(is_cite_seq=True).exists(),
            metadata=data,
            modality=modality,
            project=project,
            scpca_id=library_id,
            workflow_version=data["workflow_version"],
        )

        return library

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample) -> None:
        libraries = []
        for library_json in library_jsons:
            library_id = library_json["scpca_library_id"]
            if existing_library := Library.objects.filter(scpca_id=library_id).first():
                sample.libraries.add(existing_library)
            else:
                libraries.append(Library.get_from_dict(library_json, sample.project))

        Library.objects.bulk_create(libraries)
        sample.libraries.add(*libraries)

    @classmethod
    def load_bulk_metadata(cls, project) -> None:
        """
        Parses bulk metadata tsv files and create Library objets for bulk-only samples
        """
        if not project.has_bulk_rna_seq:
            raise Exception("Trying to load bulk libraries for project with no bulk data")

        all_bulk_libraries_metadata = metadata_parser.load_bulk_metadata(project.scpca_id)

        sample_by_id = {sample.scpca_id: sample for sample in project.samples.all()}

        for lib_metadata in all_bulk_libraries_metadata:
            if sample := sample_by_id.get(lib_metadata["scpca_sample_id"]):
                Library.bulk_create_from_dicts([lib_metadata], sample)

    @classmethod
    def load_metadata(cls, project) -> None:
        """
        Parses library metadata json files and creates Library objects.
        If the project has bulk, loads bulk libraries.
        """
        libraries_metadata = metadata_parser.load_libraries_metadata(project.scpca_id)
        library_files = OriginalFile.get_input_library_metadata_files(project.scpca_id)

        library_metadata_by_id = {
            lib_metadata["scpca_library_id"]: lib_metadata for lib_metadata in libraries_metadata
        }
        sample_by_id = {sample.scpca_id: sample for sample in project.samples.all()}

        for library_file in library_files:
            if lib_metadata := library_metadata_by_id.get(library_file.library_id):
                #  Multiplexed samples will have multiple sample IDs in lib.sample_ids
                for sample_id in library_file.sample_ids:
                    # Only create the library if the sample exists in the project
                    if sample := sample_by_id.get(sample_id):
                        Library.bulk_create_from_dicts([lib_metadata], sample)

        if project.has_bulk_rna_seq:
            Library.load_bulk_metadata(project)

    @property
    def original_files(self):
        return OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)

    @property
    def original_file_paths(self) -> List[str]:
        return sorted(self.original_files.values_list("s3_key", flat=True))

    def get_metadata(self, demux_cell_count_estimate_id) -> Dict:
        excluded_metadata_attributes = {
            "scpca_sample_id",
            "has_citeseq",
            "sample_cell_estimates",
        }
        library_metadata = {
            key: value
            for key, value in self.metadata.items()
            if key not in excluded_metadata_attributes
        }

        if self.is_multiplexed:
            library_metadata["demux_cell_count_estimate"] = self.metadata["sample_cell_estimates"][
                demux_cell_count_estimate_id
            ]

        return library_metadata

    def get_combined_library_metadata(self) -> List[Dict]:
        return [
            self.project.get_metadata() | sample.get_metadata() | self.get_metadata(sample.scpca_id)
            for sample in self.samples.all()
        ]

    def get_original_files_by_download_config(self, download_config: Dict):
        """
        Return all of a library's file paths that are suitable for the passed download config.
        """
        if download_config.get("metadata_only", False):
            return OriginalFile.objects.none()

        original_files = OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)
        if not download_config.get("includes_merged", False):
            if download_config["format"] == FileFormats.ANN_DATA:
                return original_files.exclude(is_single_cell_experiment=True)
            if download_config["format"] == FileFormats.SINGLE_CELL_EXPERIMENT:
                return original_files.exclude(is_anndata=True)

        return original_files.exclude(is_single_cell_experiment=True).exclude(is_anndata=True)

    @staticmethod
    def get_libraries_metadata(libraries) -> List[Dict]:
        return [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]

    @staticmethod
    def get_libraries_original_files(libraries, download_config):
        """
        Return file paths associated with the libraries according to the passed download_config.
        Files are then downloaded and included in computed files.
        """
        library_original_files = [
            of
            for lib in libraries
            for of in lib.get_original_files_by_download_config(download_config)
        ]

        if download_config in common.PROJECT_DOWNLOAD_CONFIGS.values():
            project = libraries.first().project
            project_original_files = [
                of for of in project.get_original_files_by_download_config(download_config)
            ]
            return project_original_files + library_original_files

        return library_original_files
