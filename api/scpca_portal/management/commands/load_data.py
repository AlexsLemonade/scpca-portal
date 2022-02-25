import csv
import json
import os
import shutil
import subprocess
from typing import Dict, List
from zipfile import ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
import botocore
from botocore.client import Config

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.management.commands.purge_project import purge_project
from scpca_portal.models import ComputedFile, Project, Sample

logger = get_and_configure_logger(__name__)
s3 = boto3.client("s3", config=Config(signature_version="s3v4"))
project_whitelist = ["murphy_chen", "green_mulcahy_levy", "dyer_chen"]

OUTPUT_DIR = "output/"
README_FILENAME = "README.md"
PROJECT_URL_TEMPLATE = "https://scpca.alexslemonade.org/projects/{project_accession}"


def purge_all_projects(should_upload):
    for project in Project.objects.all():
        purge_project(project.scpca_id, should_upload)


def package_files_for_project(
    project_dir: str,
    output_dir: str,
    project: Project,
    sample_to_file_mapping: dict,
    readme_path: str,
    should_upload: bool,
):
    zip_file_name = f"{project.scpca_id}.zip"
    project_zip = os.path.join(output_dir, zip_file_name)
    computed_file = ComputedFile(
        type="PROJECT_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=zip_file_name,
    )

    if should_upload:
        project_metadata_path = get_project_metadata_path(output_dir, project)
        with ZipFile(project_zip, "w") as zip_object:
            zip_object.write(project_metadata_path, "single_cell_metadata.tsv")
            zip_object.write(readme_path, README_FILENAME)

            if project.has_bulk_rna_seq:
                print(f"Attaching bulk data tsvs for {project.scpca_id}")
                zip_object.write(
                    get_project_bulk_metadata_path(project_dir, project), "bulk_metadata.tsv"
                )
                zip_object.write(
                    get_project_bulk_quant_path(project_dir, project), "bulk_quant.tsv"
                )

            for sample_id, file_paths in sample_to_file_mapping.items():
                for local_file_path in file_paths:
                    # We want to nest these under thier sample id.
                    archive_path = os.path.join(sample_id, os.path.basename(local_file_path))
                    zip_object.write(local_file_path, archive_path)

        computed_file.size_in_bytes = os.path.getsize(project_zip)
        s3.upload_file(project_zip, settings.AWS_S3_BUCKET_NAME, zip_file_name)
    else:
        s3_objects = s3.list_objects(Bucket=settings.AWS_S3_BUCKET_NAME, Prefix=zip_file_name)
        assert len(s3_objects["Contents"]) == 1
        computed_file.size_in_bytes = s3_objects["Contents"][0]["Size"]

    computed_file.save()

    project.computed_file = computed_file
    project.save()

    return computed_file


def get_sample_metadata_path(output_dir: str, scpca_sample_id: str):
    return os.path.join(output_dir, f"{scpca_sample_id}_libraries_metadata.tsv")


def get_project_metadata_path(output_dir: str, project: Project):
    return os.path.join(output_dir, f"{project.scpca_id}_libraries_metadata.tsv")


def get_project_bulk_metadata_path(project_dir: str, project: Project):
    return os.path.join(project_dir, f"{project.scpca_id}_bulk_metadata.tsv")


def get_project_bulk_quant_path(project_dir: str, project: Project):
    return os.path.join(project_dir, f"{project.scpca_id}_bulk_quant.tsv")


def package_files_for_sample(
    project_dir: str,
    output_dir: str,
    sample: dict,
    libraries_metadata: List[Dict],
    readme_path: str,
    should_upload: bool,
):
    sample_id = sample["scpca_sample_id"]
    libraries = [lib for lib in libraries_metadata if lib["scpca_sample_id"] == sample_id]

    zip_file_name = f"{sample_id}.zip"
    sample_zip = os.path.join(output_dir, zip_file_name)

    computed_file = ComputedFile(
        type="SAMPLE_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=zip_file_name,
    )

    file_paths = []
    if should_upload:
        with ZipFile(sample_zip, "w") as zip_object:
            local_metadata_path = get_sample_metadata_path(output_dir, sample_id)
            zip_object.write(local_metadata_path, "single_cell_metadata.tsv")
            zip_object.write(readme_path, README_FILENAME)

            for library in libraries:
                for file_postfix in ["_unfiltered.rds", "_filtered.rds", "_qc.html"]:
                    filename = f"{library['scpca_library_id']}{file_postfix}"
                    local_file_path = os.path.join(project_dir, sample_id, filename)
                    file_paths.append(local_file_path)
                    zip_object.write(local_file_path, filename)

        computed_file.size_in_bytes = os.path.getsize(sample_zip)
        s3.upload_file(sample_zip, settings.AWS_S3_BUCKET_NAME, zip_file_name)
    else:
        s3_objects = s3.list_objects(Bucket=settings.AWS_S3_BUCKET_NAME, Prefix=zip_file_name)
        assert len(s3_objects["Contents"]) == 1
        computed_file.size_in_bytes = s3_objects["Contents"][0]["Size"]

    computed_file.save()

    return computed_file, {sample_id: file_paths}


def create_sample_from_dict(project: Project, sample: dict, computed_file: ComputedFile):
    # First figure out what metadata is additional.
    # This varies project by project, so whatever's not on
    # the Sample model is additional.
    sample_columns = [
        "scpca_sample_id",
        "technologies",
        "diagnosis",
        "subdiagnosis",
        "cell_count",
        "age",
        "sex",
        "disease_timing",
        "tissue_location",
        "seq_units",
        "treatment",
        # Also include this, not because it's a sample column but
        # because we don't want it in additional_metadata.
        "scpca_library_id",
    ]
    additional_metadata = {}
    for key, value in sample.items():
        if key not in sample_columns:
            additional_metadata[key] = value

    # get_or_create returns a tuple like (object, was_created)
    sample_object = Sample(
        project=project,
        computed_file=computed_file,
        scpca_id=sample["scpca_sample_id"],
        technologies=sample["technologies"],
        diagnosis=sample["diagnosis"],
        subdiagnosis=sample["subdiagnosis"],
        age_at_diagnosis=sample["age"],
        sex=sample["sex"],
        disease_timing=sample["disease_timing"],
        tissue_location=sample["tissue_location"],
        treatment=sample.get("treatment"),
        seq_units=sample["seq_units"],
        cell_count=sample["cell_count"],
        additional_metadata=additional_metadata,
    )
    sample_object.save()

    return sample_object


def combine_and_write_metadata(
    output_dir: str, project: Project, samples_metadata: List[Dict], libraries_metadata: List[Dict]
):
    """Smush the two metadata dicts together to have all the data at
    the library level. Write the combination out at the project and
    sample level.
    """
    full_libraries_metadata = []

    # Get all the field names to pass to the csv.DictWriter
    # First, get all the field names there are.
    field_names = set(libraries_metadata[0].keys()).union(set(samples_metadata[0].keys()))
    field_names = field_names.union({"scpca_project_id", "pi_name", "project_title"})
    # Sample metadata has these at the sample level, we want it at the
    # library level.
    field_names -= {"seq_units", "technologies"}

    # Then force the following ordering:
    ordered_field_names = [
        "scpca_sample_id",
        "scpca_library_id",
        "diagnosis",
        "subdiagnosis",
        "seq_unit",
        "technology",
        "filtered_cell_count",
        "scpca_project_id",
        "pi_name",
        "project_title",
        "disease_timing",
        "age",
        "sex",
        "tissue_location",
    ]

    for field_name in ordered_field_names:
        field_names.remove(field_name)

    ordered_field_names.extend(list(field_names))

    project_metadata_path = get_project_metadata_path(output_dir, project)
    with open(project_metadata_path, "w", newline="") as project_file:
        project_writer = csv.DictWriter(
            project_file, fieldnames=ordered_field_names, delimiter="\t"
        )
        project_writer.writeheader()
        for sample in samples_metadata:
            sample_copy = sample.copy()
            sample_copy.pop("technologies")
            sample_copy.pop("seq_units")
            sample_copy["pi_name"] = project.pi_name
            sample_copy["scpca_project_id"] = project.scpca_id
            sample_copy["project_title"] = project.title

            sample_metadata_path = get_sample_metadata_path(output_dir, sample["scpca_sample_id"])
            with open(sample_metadata_path, "w", newline="") as sample_file:
                sample_writer = csv.DictWriter(
                    sample_file, fieldnames=ordered_field_names, delimiter="\t"
                )
                sample_writer.writeheader()
                for library in libraries_metadata:
                    if library["scpca_sample_id"] == sample["scpca_sample_id"]:
                        library.update(sample_copy)
                        full_libraries_metadata.append(library)
                        project_writer.writerow(library)
                        sample_writer.writerow(library)

    return full_libraries_metadata


def load_data_for_project(
    data_dir: str, output_dir: str, project: Project, readme_text: str, should_upload: bool
):
    project_dir = f"{data_dir}{project.scpca_id}/"

    project_url = PROJECT_URL_TEMPLATE.format(project_accession=project.scpca_id)
    formatted_readme = readme_text.format(
        project_accession=project.scpca_id, project_url=project_url
    )

    readme_path = os.path.join(output_dir, README_FILENAME)
    with open(readme_path, "w") as readme_file:
        readme_file.write(formatted_readme)

    samples_metadata = []
    try:
        with open(project_dir + "samples_metadata.csv") as csvfile:
            samples_metadata = [line for line in csv.DictReader(csvfile)]
    except botocore.exceptions.ClientError:
        print(f"No samples_metadata.csv found for project {project.scpca_id}.")
        return

    libraries_metadata = []

    for sample in samples_metadata:
        sample_cell_count = 0
        sample_technologies = set()
        sample_seq_units = set()
        sample_dir = os.path.join(project_dir, sample["scpca_sample_id"])

        for filename in os.listdir(sample_dir):
            if filename.endswith("_metadata.json"):
                with open(os.path.join(sample_dir, filename)) as json_file:
                    parsed_json = json.load(json_file)

                    # Rename these key for consistency with the docs:
                    parsed_json["scpca_sample_id"] = parsed_json.pop("sample_id")
                    parsed_json["scpca_library_id"] = parsed_json.pop("library_id")
                    parsed_json["filtered_cell_count"] = parsed_json.pop("filtered_cells")

                    libraries_metadata.append(parsed_json)

                    sample_cell_count += parsed_json["filtered_cell_count"]
                    sample_technologies.add(parsed_json["technology"].strip())
                    sample_seq_units.add(parsed_json["seq_unit"].strip())

        sample["cell_count"] = sample_cell_count
        sample["technologies"] = ", ".join(sample_technologies)
        sample["seq_units"] = ", ".join(sample_seq_units)

    full_libraries_metadata = combine_and_write_metadata(
        output_dir, project, samples_metadata, libraries_metadata
    )

    created_samples = []
    sample_to_file_mapping = {}
    for sample in samples_metadata:
        computed_file, sample_files = package_files_for_sample(
            project_dir, output_dir, sample, full_libraries_metadata, readme_path, should_upload,
        )

        sample_object = create_sample_from_dict(project, sample, computed_file)
        created_samples.append(sample_object)

        sample_to_file_mapping.update(sample_files)

    package_files_for_project(
        project_dir, output_dir, project, sample_to_file_mapping, readme_path, should_upload,
    )

    return created_samples


def load_data_from_s3(
    should_upload: bool,
    reload_existing: bool,
    reload_all: bool,
    input_bucket_name="scpca-portal-inputs",
    data_dir="/home/user/data/",
    readme_path="/home/user/scpca_portal/config/readme_template.md",
):

    if reload_all:
        purge_all_projects(should_upload)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # If this raises we're done anyway, so let it.
    command_list = ["aws", "s3", "sync", "--delete", f"s3://{input_bucket_name}", data_dir]
    if "public-test" in input_bucket_name:
        command_list.append("--no-sign-request")

    subprocess.check_call(command_list)

    # Make sure we're starting with a blank slate for the zip files.
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.mkdir(OUTPUT_DIR)

    with open(readme_path) as readme_file:
        readme_text = readme_file.read()

    project_input_metadata_file = "project_metadata.csv"
    project_input_metadata_path = f"{data_dir}{project_input_metadata_file}"

    with open(project_input_metadata_path) as csvfile:
        projects = csv.DictReader(csvfile)
        for project in projects:
            if project["submitter"] not in project_whitelist:
                continue

            scpca_id = project["scpca_project_id"]

            if reload_existing:
                # Purge existing projects so they can be readded.
                existing_project = Project.objects.filter(scpca_id=scpca_id).first()

                if existing_project:
                    purge_project(scpca_id, should_upload)

            # check if there is bulk metadata
            has_bulk_rna_seq = False
            bulk_metadata = f"{data_dir}{scpca_id}/{scpca_id}_bulk_metadata.tsv"

            if os.path.exists(bulk_metadata):
                has_bulk_rna_seq = True

            project, created = Project.objects.get_or_create(
                scpca_id=scpca_id,
                pi_name=project["submitter"],
                human_readable_pi_name=project["PI"],
                title=project["project_title"],
                abstract=project["abstract"],
                contact_name=project["contact_name"],
                contact_email=project["contact_email"],
                has_bulk_rna_seq=has_bulk_rna_seq,
            )

            if not created:
                # Only import new projects. If old ones are desired
                # they should be purged and readded.
                continue

            if project.scpca_id in os.listdir(data_dir):
                print(f"Importing and loading data for project {project.scpca_id}")
                created_samples = load_data_for_project(
                    data_dir, OUTPUT_DIR, project, readme_text, should_upload
                )

                print(f"created {len(created_samples)} samples for project {project.scpca_id}")
            else:
                print(
                    f"Metadata found for project {project.scpca_id} "
                    f"but no s3 folder of that name exists."
                )


class Command(BaseCommand):
    help = """Populates the database with data.

    The data should be contained in an S3 bucket called scpca-portal-inputs.

    The directory structure for this bucket should follow this pattern:
        /project_metadata.csv
        /SCPCP000001/libraries_metadata.csv
        /SCPCP000001/samples_metadata.csv
        /SCPCP000001/SCPCS000109/SCPCL000126_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000126_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000126_metadata.json
        /SCPCP000001/SCPCS000109/SCPCL000127_filtered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_unfiltered.rds
        /SCPCP000001/SCPCS000109/SCPCL000127_qc.html
        /SCPCP000001/SCPCS000109/SCPCL000127_metadata.json

    The files will be zipped up and stats will be calculated for them.

    If run locally the zipped ComputedFiles will be copied to the
    "scpca-local-data" bucket.

    If run in the cloud the zipped ComputedFiles files will be copied
    to a stack-specific S3 bucket."""

    def add_arguments(self, parser):
        parser.add_argument("--reload-existing", action="store_true")
        parser.add_argument("--reload-all", action="store_true")
        parser.add_argument("--upload", default=settings.UPDATE_IMPORTED_DATA, type=bool)

    def handle(self, *args, **options):

        # locally the docker container puts the code in a folder called code
        # this allows us to run the same command on production or locally
        code_dir = "/home/user/code/{}" if os.path.exists("/home/user/code") else "/home/user/{}"

        load_data_from_s3(
            options["upload"],
            options["reload_existing"],
            options["reload_all"],
            "scpca-portal-inputs",
            code_dir.format("data/"),
            code_dir.format("scpca_portal/config/readme_template.md"),
        )
