import csv
import os
import shutil
import subprocess
from zipfile import ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand

import boto3
import botocore
from botocore.client import Config

from scpca_portal.models import ComputedFile, Project, Sample

s3 = boto3.client("s3", config=Config(signature_version="s3v4"))


def package_files_for_project(
    project_dir, output_dir, project, sample_to_file_mapping, project_metadata_path, should_zip_data
):
    zip_file_name = f"{project.pi_name}_project.zip"
    project_zip = os.path.join(output_dir, zip_file_name)

    if should_zip_data:
        with ZipFile(project_zip, "w") as zip_object:
            zip_object.write(project_metadata_path, "libraries_metadata.csv")

            for sample_id, file_paths in sample_to_file_mapping.items():
                for local_file_path in file_paths:
                    # We want to nest these under thier sample id.
                    archive_path = os.path.join(sample_id, os.path.basename(local_file_path))
                    zip_object.write(local_file_path, archive_path)

        s3.upload_file(project_zip, settings.AWS_S3_BUCKET_NAME, zip_file_name)

    computed_file = ComputedFile(
        type="PROJECT_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=zip_file_name,
    )
    computed_file.save()

    project.computed_file = computed_file
    project.save()

    return computed_file


def get_sample_metadata_path(output_dir, scpca_sample_id):
    return os.path.join(output_dir, f"{scpca_sample_id}_libraries_metadata.csv")


def package_files_for_sample(project_dir, output_dir, sample, libraries_metadata, should_zip_data):
    sample_id = sample["scpca_sample_id"]
    libraries = [lib for lib in libraries_metadata if lib["scpca_sample_id"] == sample_id]

    zip_file_name = f"{sample_id}.zip"
    sample_zip = os.path.join(output_dir, zip_file_name)

    file_paths = []
    if should_zip_data:
        with ZipFile(sample_zip, "w") as zip_object:
            local_metadata_path = get_sample_metadata_path(output_dir, sample_id)
            zip_object.write(local_metadata_path, "libraries_metadata.csv")

            for library in libraries:
                # TODO: reenable _qc_report.html once it's there.
                # https://github.com/AlexsLemonade/scpca-portal/issues/33
                # for file_postfix in ["_unfiltered_sce.rds", "_filtered_sce.rds", "_qc_report.html"]:
                for file_postfix in ["_unfiltered_sce.rds", "_filtered_sce.rds"]:
                    filename = f"{library['scpca_library_id']}{file_postfix}"
                    local_file_path = os.path.join(project_dir, "files", sample_id, filename)
                    file_paths.append(local_file_path)
                    zip_object.write(local_file_path, filename)

        s3.upload_file(sample_zip, settings.AWS_S3_BUCKET_NAME, zip_file_name)

    computed_file = ComputedFile(
        type="SAMPLE_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=zip_file_name,
    )
    computed_file.save()

    return computed_file, {sample_id: file_paths}


def create_sample_from_dict(project, sample, computed_file):
    # First figure out what metadata is additional.
    # This varies project by project, so whatever's not on
    # the Sample model is additional.
    sample_columns = [
        "scpca_sample_id",
        "technologies",
        "Diagnosis",
        "Subdiagnosis",
        "Age at Diagnosis",
        "Sex",
        "Disease Timing",
        "Tissue Location",
        "treatment",
        "seq_units",
    ]
    additional_metadata = {}
    for key, value in sample.items():
        if key not in sample_columns:
            additional_metadata[key] = value

    # get_or_create returns a tuple like (object, was_created)
    sample_object = Sample(
        project=project,
        computed_file=computed_file,
        scpca_sample_id=sample["scpca_sample_id"],
        technologies=sample["technologies"],
        diagnosis=sample["Diagnosis"],
        subdiagnosis=sample["Subdiagnosis"],
        age_at_diagnosis=sample["Age at Diagnosis"],
        sex=sample["Sex"],
        disease_timing=sample["Disease Timing"],
        tissue_location=sample["Tissue Location"],
        treatment=sample["Treatment"],
        seq_units=sample["seq_units"],
        additional_metadata=additional_metadata,
    )
    sample_object.save()

    return sample_object


def load_data_for_project(data_dir, output_dir, project, should_zip_data):
    # Don't update existing Samples, that's error
    # prone. If there's samples that need to be updated
    # they should be purged and readded.
    # TODO: purge projects before loading data for them.

    project_dir = f"{data_dir}{project.pi_name}/"

    libraries_metadata = []
    try:
        with open(project_dir + "libraries_metadata.csv") as csvfile:
            libraries_metadata = [line for line in csv.DictReader(csvfile)]
    except botocore.exceptions.ClientError:
        print(f"No libraries_metadata.csv found for project {project.pi_name}.")
        return

    samples_metadata = []
    try:
        with open(project_dir + "samples_metadata.csv") as csvfile:
            samples_metadata = [line for line in csv.DictReader(csvfile)]
    except botocore.exceptions.ClientError:
        print(f"No samples_metadata.csv found for project {project.pi_name}.")
        return

    # Smush the two metadata dicts together to have all the data at
    # the library level. Write the combination out at the project and
    # sample level.
    full_libraries_metadata = []

    # First get the field names to pass to the csv.DictWriter
    field_names = set(libraries_metadata[0].keys()).union(set(samples_metadata[0].keys()))
    field_names = field_names.union({"pi_name", "project_title"})
    # Sample metadata has these at the sample level, we want it at the
    # library level.
    field_names -= {"seq_units", "technologies"}
    field_names = list(field_names)
    # TODO: order these?

    project_metadata_path = os.path.join(output_dir, f"{project.pi_name}_libraries_metadata.csv")
    with open(project_metadata_path, "w", newline="") as project_file:
        project_writer = csv.DictWriter(project_file, fieldnames=field_names)
        project_writer.writeheader()
        for sample in samples_metadata:
            sample_copy = sample.copy()
            sample_copy.pop("scpca_library_id")
            sample_copy.pop("seq_units")
            sample_copy.pop("technologies")
            sample_copy["pi_name"] = project.pi_name
            sample_copy["project_title"] = project.title

            sample_metadata_path = get_sample_metadata_path(output_dir, sample["scpca_sample_id"])
            with open(sample_metadata_path, "w", newline="") as sample_file:
                sample_writer = csv.DictWriter(sample_file, fieldnames=field_names)
                sample_writer.writeheader()
                for library in libraries_metadata:
                    if library["scpca_sample_id"] == sample["scpca_sample_id"]:
                        library.update(sample_copy)
                        full_libraries_metadata.append(library)
                        project_writer.writerow(library)
                        sample_writer.writerow(library)

    created_samples = []
    sample_to_file_mapping = {}
    for sample in samples_metadata:
        computed_file, sample_files = package_files_for_sample(
            project_dir, output_dir, sample, full_libraries_metadata, should_zip_data
        )

        sample_object = create_sample_from_dict(project, sample, computed_file)
        created_samples.append(sample_object)

        sample_to_file_mapping.update(sample_files)

    package_files_for_project(
        project_dir,
        output_dir,
        project,
        sample_to_file_mapping,
        project_metadata_path,
        should_zip_data,
    )

    return created_samples


def load_data_from_s3(
    should_update, bucket_name="scpca-portal-inputs", data_dir="/home/user/data/"
):
    # should_update could be False, True, or None.
    # If None then the default behavior is based on prod vs local.
    if should_update is False:
        should_zip_data = False
    elif should_update:
        should_zip_data = True
    else:
        should_zip_data = settings.UPDATE_IMPORTED_DATA

    # If this raises we're done anyway, so let it.
    subprocess.check_call(["aws", "s3", "sync", f"s3://{bucket_name}", data_dir])

    # Make sure we're starting with a blank slate for the zip files.
    output_dir = "output/"
    shutil.rmtree(output_dir, ignore_errors=True)
    os.mkdir(output_dir)

    project_metadata_file = "project_metadata.csv"
    project_metadata_path = f"{data_dir}{project_metadata_file}"

    with open(project_metadata_path) as csvfile:
        projects = csv.DictReader(csvfile)
        for project in projects:
            Project.objects.get_or_create(
                pi_name=project["PI Name"],
                title=project["Project Title"],
                abstract=project["Abstract"],
                contact=project["Project Contact"],
            )

    for project_dir in os.listdir():
        project = Project.objects.filter(pi_name=project_dir).first()
        if project_dir != project_metadata_file and project:
            print(f"Importing and loading data for project {project_dir}")
            created_samples = load_data_for_project(data_dir, output_dir, project, should_zip_data)

            print(f"created {len(created_samples)} samples for project {project_dir}")


class Command(BaseCommand):
    help = """Populates the database with data.

    The data should be contained in an S3 bucket called scpca-portal-inputs.

    The directory structure for this bucket should follow this pattern:
        /project_metadata.csv
        /dyer_chen/libraries_metadata.csv
        /dyer_chen/samples_metadata.csv
        /dyer_chen/files/SCPCS000109/SCPCL000126_filtered_sce.rds
        /dyer_chen/files/SCPCS000109/SCPCL000126_unfiltered_sce.rds
        /dyer_chen/files/SCPCS000109/SCPCL000126_qc_report.html
        /dyer_chen/files/SCPCS000109/SCPCL000127_filtered_sce.rds
        /dyer_chen/files/SCPCS000109/SCPCL000127_unfiltered_sce.rds
        /dyer_chen/files/SCPCS000109/SCPCL000127_qc_report.html

    The files will be zipped up and stats will be calculated for them.

    If run locally the zipped ComputedFiles will be copied to the
    "scpca-local-data" bucket.

    If run in the cloud the zipped ComputedFiles files will be copied
    to a stack-specific S3 bucket."""

    def add_arguments(self, parser):
        parser.add_argument("--update", default=None, type=bool)

    def handle(self, *args, **options):
        load_data_from_s3(options["update"])
