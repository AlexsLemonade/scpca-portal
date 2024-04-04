import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zipfile import ZipFile
from typing import Dict, List

import boto3
from botocore.client import Config

from scpca_portal import common, utils
from scpca_portal.models import Sample
from scpca_portal.models.computed_file import ComputedFile


"""
The goal of this file is 3-fold:
- To creates relevant readmes,
- To handle input of individual computed file metadata into the db,
- To create a zip archive of relevant files to be uploaded to an S3 output bucket. 
"""

logger = logging.getLogger()

# Is this line necessary as its already excited in the load_data command which preceeds this classes usage?
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


class FileArchiver():
    def archive_file(
        self,
        combined_single_cell_metadata: List[Dict],
        combined_spatial_metadata: List[Dict],
        combined_multiplexed_metadata: List[Dict],
        **kwargs
    ):
        single_cell_file_mapping = {
            ComputedFile.OutputFileFormats.ANN_DATA: {},
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        single_cell_workflow_versions = set()        

        spatial_file_mapping = {
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        spatial_workflow_versions = set()

        multiplexed_file_mapping = {
            ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT: {},
        }
        multiplexed_workflow_versions = set()

        def update_ann_data(future):
            computed_file, metadata_files = future.result()
            single_cell_file_mapping[ComputedFile.OutputFileFormats.ANN_DATA].update(metadata_files)
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_multiplexed_data(future):
            computed_file, metadata_files = future.result()
            multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_single_cell_data(future):
            computed_file, metadata_files = future.result()
            single_cell_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        def update_spatial_data(future):
            computed_file, metadata_files = future.result()
            spatial_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                metadata_files
            )
            self.process_computed_file(
                computed_file, kwargs["clean_up_output_data"], kwargs["update_s3"]
            )

        max_workers = kwargs["max_workers"]
        samples = Sample.objects.filter(project__scpca_id=kwargs["scpca_project_id"])
        samples_count = len(samples)
        logger.info(
            f"Processing {samples_count} sample{pluralize(samples_count)} using "
            f"{max_workers} worker{pluralize(max_workers)}"
        )
        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for sample in samples:
                # Skip computed files creation if sample directory does not exist.
                if sample.scpca_id not in non_downloadable_sample_ids:
                    libraries = [
                        library
                        for library in combined_single_cell_metadata
                        if library["scpca_sample_id"] == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    single_cell_workflow_versions.update(workflow_versions)

                    file_formats = [ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT]
                    if sample.includes_anndata:
                        file_formats.append(ComputedFile.OutputFileFormats.ANN_DATA)

                    for file_format in file_formats:
                        tasks.submit(
                            ComputedFile.get_sample_single_cell_file,
                            sample,
                            libraries,
                            workflow_versions,
                            file_format,
                        ).add_done_callback(
                            update_single_cell_data
                            if file_format == ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT
                            else update_ann_data
                        )

                        if sample.has_spatial_data:
                            libraries = [
                                library
                                for library in combined_spatial_metadata
                                if library["scpca_sample_id"] == sample.scpca_id
                            ]
                            workflow_versions = [
                                library["workflow_version"] for library in libraries
                            ]
                            spatial_workflow_versions.update(workflow_versions)
                            tasks.submit(
                                ComputedFile.get_sample_spatial_file,
                                sample,
                                libraries,
                                workflow_versions,
                                ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                            ).add_done_callback(update_spatial_data)

                if sample.has_multiplexed_data:
                    libraries = [
                        library
                        for library in combined_multiplexed_metadata
                        if library.get("scpca_sample_id") == sample.scpca_id
                    ]
                    workflow_versions = [library["workflow_version"] for library in libraries]
                    multiplexed_workflow_versions.update(workflow_versions)
                    tasks.submit(
                        ComputedFile.get_sample_multiplexed_file,
                        sample,
                        libraries,
                        multiplexed_library_path_mapping,
                        workflow_versions,
                        ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
                    ).add_done_callback(update_multiplexed_data)

        if multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT]:
            # We want a single ZIP archive for a multiplexed samples project.
            multiplexed_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT].update(
                single_cell_file_mapping[ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT]
            )
        self.create_computed_files(
            single_cell_file_mapping,
            single_cell_workflow_versions,
            spatial_file_mapping,
            spatial_workflow_versions,
            multiplexed_file_mapping,
            multiplexed_workflow_versions,
            clean_up_output_data=kwargs["clean_up_output_data"],
            update_s3=kwargs["update_s3"],
        )

        # Set modality flags based on a real data availability.
        self.has_bulk_rna_seq = self.samples.filter(has_bulk_rna_seq=True).exists()
        self.has_cite_seq_data = self.samples.filter(has_cite_seq_data=True).exists()
        self.has_multiplexed_data = self.samples.filter(has_multiplexed_data=True).exists()
        self.has_single_cell_data = self.samples.filter(has_single_cell_data=True).exists()
        self.has_spatial_data = self.samples.filter(has_spatial_data=True).exists()
        self.includes_anndata = self.samples.filter(includes_anndata=True).exists()
        self.save(
            update_fields=(
                "has_bulk_rna_seq",
                "has_cite_seq_data",
                "has_multiplexed_data",
                "has_single_cell_data",
                "has_spatial_data",
                "includes_anndata",
            )
        )

    @property
    def output_single_cell_computed_file_name(scpca_id):
        return f"{scpca_id}.zip"

    @property
    def output_single_cell_anndata_computed_file_name(scpca_id):
        return f"{scpca_id}_anndata.zip"

    @property
    def output_spatial_computed_file_name(scpca_id):
        return f"{scpca_id}_spatial.zip"

    @property
    def output_multiplexed_computed_file_name(scpca_id):
        return f"{scpca_id}_multiplexed.zip"

    @property
    def zip_file_path(self):
        return common.OUTPUT_DATA_PATH / self.s3_key

    def create_computed_files(
        self,
        single_cell_file_mapping,
        single_cell_workflow_versions,
        spatial_file_mapping,
        spatial_workflow_versions,
        multiplexed_file_mapping,
        multiplexed_workflow_versions,
        max_workers=6,  # 6 = 2 file formats * 3 mappings.
        clean_up_output_data=True,
        update_s3=False,
    ):
        """Prepares ready for saving project computed files based on generated file mappings."""

        def create_computed_file(future):
            computed_file = future.result()
            self.process_computed_file(computed_file, clean_up_output_data, update_s3)

        with ThreadPoolExecutor(max_workers=max_workers) as tasks:
            for file_format in (
                ComputedFile.OutputFileFormats.ANN_DATA,
                ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT,
            ):
                if multiplexed_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_multiplexed_file,
                        self,
                        multiplexed_file_mapping,
                        multiplexed_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

                if single_cell_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_single_cell_file,
                        self,
                        single_cell_file_mapping,
                        single_cell_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

                if spatial_file_mapping.get(file_format):
                    tasks.submit(
                        ComputedFile.get_project_spatial_file,
                        self,
                        spatial_file_mapping,
                        spatial_workflow_versions,
                        file_format,
                    ).add_done_callback(create_computed_file)

    def get_project_single_cell_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined single cell data."""

        if file_format == cls.OutputFileFormats.ANN_DATA:
            computed_file_name = project.output_single_cell_anndata_computed_file_name
            readme_file_path = ComputedFile.README_ANNDATA_FILE_PATH
        else:
            computed_file_name = project.output_single_cell_computed_file_name
            readme_file_path = ComputedFile.README_SINGLE_CELL_FILE_PATH

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=computed_file_name,
            type=cls.OutputFileTypes.PROJECT_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(readme_file_path, ComputedFile.OUTPUT_README_FILE_NAME)
            zip_file.write(
                project.output_single_cell_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                for file_path in file_paths:
                    # Nest these under their sample id.
                    zip_file.write(file_path, Path(sample_id, file_path.name))

            if project.has_bulk_rna_seq:
                zip_file.write(project.input_bulk_metadata_file_path, "bulk_metadata.tsv")
                zip_file.write(project.input_bulk_quant_file_path, "bulk_quant.tsv")

        computed_file.has_bulk_rna_seq = project.has_bulk_rna_seq
        computed_file.has_cite_seq_data = project.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    def get_project_spatial_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined spatial data."""

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SPATIAL,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=project.output_spatial_computed_file_name,
            type=cls.OutputFileTypes.PROJECT_SPATIAL_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SPATIAL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                project.output_spatial_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                sample_path = project.get_sample_input_data_dir(sample_id)
                for file_path in file_paths:
                    zip_file.write(file_path, Path(file_path).relative_to(sample_path))

        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    def get_project_multiplexed_file(
        cls, project, sample_to_file_mapping, workflow_versions, file_format
    ):
        """Prepares a ready for saving single data file of project's combined multiplexed data."""

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.MULTIPLEXED,
            project=project,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=project.output_multiplexed_computed_file_name,
            type=cls.OutputFileTypes.PROJECT_MULTIPLEXED_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_MULTIPLEXED_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                project.output_multiplexed_metadata_file_path, computed_file.metadata_file_name
            )

            for sample_id, file_paths in sample_to_file_mapping[file_format].items():
                for file_path in file_paths:
                    # Nest these under their sample id.
                    zip_file.write(file_path, Path(sample_id, file_path.name))

            if project.has_bulk_rna_seq:
                zip_file.write(project.input_bulk_metadata_file_path, "bulk_metadata.tsv")
                zip_file.write(project.input_bulk_quant_file_path, "bulk_quant.tsv")

        computed_file.has_bulk_rna_seq = project.has_bulk_rna_seq
        computed_file.has_cite_seq_data = project.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file

    def get_sample_single_cell_file(cls, sample, libraries, workflow_versions, file_format):
        """
        Prepares a ready for saving single data file of sample's combined single cell data.
        Returns the data file and file mapping for a sample.
        """
        is_anndata_file_format = file_format == cls.OutputFileFormats.ANN_DATA
        if is_anndata_file_format:
            file_name = sample.output_single_cell_anndata_computed_file_name
            common_file_suffixes = (
                "filtered_rna.hdf5",
                "processed_rna.hdf5",
                "qc.html",
                "unfiltered_rna.hdf5",
            )
        else:
            file_name = sample.output_single_cell_computed_file_name
            common_file_suffixes = (
                "filtered.rds",
                "processed.rds",
                "qc.html",
                "unfiltered.rds",
            )
        cite_seq_anndata_file_suffixes = (
            "filtered_adt.hdf5",
            "processed_adt.hdf5",
            "unfiltered_adt.hdf5",
        )

        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SINGLE_CELL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SINGLE_CELL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                sample.output_single_cell_metadata_file_path,
                ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME,
            )

            for library in libraries:
                file_suffixes = (
                    common_file_suffixes + cite_seq_anndata_file_suffixes
                    if is_anndata_file_format and library.get("has_citeseq")
                    else common_file_suffixes
                )
                for file_suffix in file_suffixes:
                    file_name = f"{library['scpca_library_id']}_{file_suffix}"
                    file_path = (
                        sample.project.get_sample_input_data_dir(sample.scpca_id) / file_name
                    )
                    file_paths.append(file_path)
                    zip_file.write(file_path, file_name)

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = sample.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {sample.scpca_id: file_paths}

    def get_sample_spatial_file(cls, sample, libraries, workflow_versions, file_format):
        """
        Prepares a ready for saving single data file of sample's combined spatial data.
        Returns the data file and file mapping for a sample.
        """
        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.SPATIAL,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=sample.output_spatial_computed_file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_SPATIAL_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_paths = []
        with ZipFile(computed_file.zip_file_path, "w") as zip_file:
            zip_file.write(
                ComputedFile.README_SPATIAL_FILE_PATH,
                ComputedFile.OUTPUT_README_FILE_NAME,
            )
            zip_file.write(
                sample.output_spatial_metadata_file_path,
                ComputedFile.MetadataFilenames.SPATIAL_METADATA_FILE_NAME,
            )

            for library in libraries:
                library_path = Path(
                    sample.project.get_sample_input_data_dir(sample.scpca_id),
                    f"{library['scpca_library_id']}_spatial",
                )
                for item in library_path.rglob("*"):  # Add the entire directory contents.
                    zip_file.write(item, item.relative_to(library_path.parent))
                    file_paths.append(f"{Path(library_path, item.relative_to(library_path))}")

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = False  # Spatial downloads can't contain CITE-seq data.
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {sample.scpca_id: file_paths}

    def get_sample_multiplexed_file(
        cls, sample, libraries, library_path_mapping, workflow_versions, file_format
    ):
        """
        Prepares a ready for saving single data file of sample's combined multiplexed data.
        Returns the data file and file mapping for a sample.
        """
        computed_file = cls(
            format=file_format,
            modality=cls.OutputFileModalities.MULTIPLEXED,
            s3_bucket=settings.AWS_S3_BUCKET_NAME,
            s3_key=sample.output_multiplexed_computed_file_name,
            sample=sample,
            type=cls.OutputFileTypes.SAMPLE_MULTIPLEXED_ZIP,
            workflow_version=utils.join_workflow_versions(workflow_versions),
        )

        file_name_path_mapping = {}
        for library in libraries:
            library_id = library["scpca_library_id"]
            for file_suffix in ("_filtered.rds", "_processed.rds", "_qc.html", "_unfiltered.rds"):
                file_name = f"{library_id}{file_suffix}"
                file_name_path_mapping[file_name] = Path(
                    library_path_mapping[library_id], file_name
                )

        if not computed_file.zip_file_path.exists():
            with ZipFile(computed_file.zip_file_path, "w") as zip_file:
                zip_file.write(
                    ComputedFile.README_MULTIPLEXED_FILE_PATH,
                    ComputedFile.OUTPUT_README_FILE_NAME,
                )
                zip_file.write(
                    sample.output_multiplexed_metadata_file_path,
                    ComputedFile.MetadataFilenames.SINGLE_CELL_METADATA_FILE_NAME,
                )
                for file_name, file_path in file_name_path_mapping.items():
                    zip_file.write(file_path, file_name)

        computed_file.has_bulk_rna_seq = False  # Sample downloads can't contain bulk data.
        computed_file.has_cite_seq_data = sample.has_cite_seq_data
        computed_file.size_in_bytes = computed_file.zip_file_path.stat().st_size

        return computed_file, {"_".join(sample.multiplexed_ids): file_name_path_mapping.values()}
