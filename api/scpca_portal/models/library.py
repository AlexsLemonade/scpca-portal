from typing import TYPE_CHECKING, Dict, List, Self

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import QuerySet

from scpca_portal import metadata_parser
from scpca_portal.enums import FileFormats, Modalities
from scpca_portal.models.loadable_resource_abc import LoadableResourceABC
from scpca_portal.models.original_file import OriginalFile

if TYPE_CHECKING:
    from api.scpca_portal.models import Project, Sample


class Library(LoadableResourceABC):
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

    def __str__(self) -> str:
        return f"Library {self.scpca_id}"

    # TODO: remove before loadable resource feature branch lands
    @classmethod
    def get_from_dict(cls, data: Dict, project: "Project") -> Self:
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

    def update_from_dict(self, data: Dict) -> Self:
        original_files = OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)

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

        self.formats = sorted(formats)
        self.is_multiplexed = data.get("is_multiplexed", False)
        self.has_cite_seq_data = original_files.filter(is_cite_seq=True).exists()
        self.metadata = data
        self.modality = modality
        self.workflow_version = data["workflow_version"]

        return self

    @classmethod
    def bulk_create_from_dicts(cls, library_jsons: List[Dict], sample: "Sample") -> None:
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
    def get_all_input_metadata_files(cls) -> QuerySet[OriginalFile]:
        return OriginalFile.get_all_input_library_metadata_files_with_bulk()

    @classmethod
    def get_metadata_dicts_by_id(
        cls, *, resources: QuerySet[LoadableResourceABC] | None = None
    ) -> Dict[str, Dict]:
        kwargs = {}
        if resources:
            kwargs["library_ids"] = set(resources.values_list("scpca_id", flat=True))
        libraries_metadata = metadata_parser.load_all_libraries_metadata_with_bulk(**kwargs)
        return {md["scpca_library_id"]: md for md in libraries_metadata}

    # TODO: remove before loadable resource feature branch lands
    @classmethod
    def load_bulk_metadata(cls, project: "Project") -> None:
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

    # TODO: remove before loadable resource feature branch lands
    @classmethod
    def load_metadata(cls, project: "Project") -> None:
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

    @classmethod
    def create_new_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> None:
        existing_library_ids = set(cls.objects.values_list("scpca_id", flat=True))
        new_library_sample_project_id_tuples = set(
            OriginalFile.objects.exclude(library_id__isnull=True)
            .exclude(library_id__in=existing_library_ids)
            .values_list("library_id", "sample_ids", "project_id")
            .distinct()
        )
        new_metadata_library_sample_project_id_tuples = set(
            (library_id, sample_id, project_id)
            for project_id, sample_id, library_id in cls.get_metadata_id_tuples(
                metadata_dicts_by_ids.values()
            )
            if library_id not in existing_library_ids
        )
        new_library_sample_project_id_tuples = (
            new_library_sample_project_id_tuples | new_metadata_library_sample_project_id_tuples
        )

        if not new_library_sample_project_id_tuples:
            return

        # Resolve Project via the FK's related_model
        # to avoid a circular import (Project already imports Library)
        Project = cls._meta.get_field("project").related_model
        projects_by_id = Project.objects.in_bulk(
            [project_id for _, _, project_id in new_library_sample_project_id_tuples],
            field_name="scpca_id",
        )

        new_libraries = cls.objects.bulk_create(
            cls(scpca_id=new_library_id, project=projects_by_id[project_id])
            for new_library_id, sample_ids, project_id in new_library_sample_project_id_tuples
        )
        libraries_by_id = {library.scpca_id: library for library in new_libraries}

        # Resolve Sample via the many-to-many's related_model
        # to avoid a circular import (Sample already imports Library)
        Sample = cls._meta.get_field("samples").related_model
        associated_sample_ids = {
            sample_id
            for _, sample_ids, _ in new_library_sample_project_id_tuples
            for sample_id in sample_ids
        }
        samples_by_id = Sample.objects.in_bulk(associated_sample_ids, field_name="scpca_id")

        for library_id, sample_ids, _ in new_library_sample_project_id_tuples:
            library_samples = [samples_by_id[sample_id] for sample_id in sample_ids]
            libraries_by_id[library_id].samples.add(*library_samples)

    @classmethod
    def remove_deleted_objects(cls, metadata_dicts_by_ids: Dict[str, Dict]) -> None:
        # TODO: before merging feature into dev: need to clarify mechanism to alert user datasets
        existing_library_ids = set(
            OriginalFile.objects.exclude(library_id__isnull=True).values_list(
                "library_id", flat=True
            )
        ) | set(metadata_dicts_by_ids.keys())

        cls.objects.exclude(scpca_id__in=existing_library_ids).delete()

    @staticmethod
    def get_lockfile_filter_kwargs(lockfile_project_ids: List) -> Dict:
        return {"project__scpca_id__in": lockfile_project_ids}

    @property
    def original_files(self) -> QuerySet[OriginalFile]:
        return OriginalFile.downloadable_objects.filter(library_id=self.scpca_id)

    @property
    def original_file_paths(self) -> List[str]:
        return sorted(self.original_files.values_list("s3_key", flat=True))

    @property
    def loaded_original_files(self) -> QuerySet[OriginalFile]:
        """
        This property returns all files associated with the library, whether downloadable or not.
        """
        return OriginalFile.objects.filter(library_id=self.scpca_id)

    def get_metadata(self, demux_cell_count_estimate_id: str) -> Dict:
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

    @staticmethod
    def get_libraries_metadata(libraries: QuerySet[Self]) -> List[Dict]:
        return [
            lib_md for library in libraries for lib_md in library.get_combined_library_metadata()
        ]
