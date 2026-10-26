"""
Shared utilities for the test_*_loadable_resource.py files, which run the real reload pipeline
against the test S3 bucket.

A test only needs a few resources, not the whole bucket. Each wrapper here builds a side_effect
that a test patches over a real function: it calls the real function, then narrows the output to
the requested ids of a given resource_cls (Project, Sample or Library).
- filter_original_files_by_resource_wrapper patches OriginalFile.get_syncable_files, scoping which
  files sync_original_files syncs.
- filter_metadata_by_resource_wrapper patches the metadata_parser load_all_* functions, scoping
  which metadata sync_model reads. It can also add or modify a row to simulate bucket changes.

TestLoadableResourceABCUtils at the bottom checks the wrappers in isolation against mocked inputs.
"""

from typing import Dict, List
from unittest.mock import patch

from django.test import TestCase

from scpca_portal import metadata_parser
from scpca_portal.models import Library, OriginalFile, Project, Sample

# Capture the real (bound) functions before any patching occurs.
# Must run at import time. Capturing while a patch is active would
# grab the mocked function instead, causing infinite recursion.
non_patched_get_syncable_files = OriginalFile.get_syncable_files
non_patched_load_all_projects_metadata = metadata_parser.load_all_projects_metadata
non_patched_load_all_samples_metadata = metadata_parser.load_all_samples_metadata
non_patched_load_all_libraries_metadata = metadata_parser.load_all_libraries_metadata
non_patched_load_all_bulk_libraries_metadata = metadata_parser.load_all_bulk_libraries_metadata


def filter_original_files_by_resource_wrapper(resource_cls: type, resource_ids: List[str]):
    """
    Build a side_effect for patching OriginalFile.get_syncable_files. It delegates to the real
    implementation, then narrows the result to resource_ids.

    Project keeps every file and lockfile in the requested projects. Sample and Library narrow only
    their own tier of files and always keep project-level files and lockfiles. A bulk resource has
    no file carrying its id, only a row in a project-level metadata file, so that file must always
    sync.
    """

    if resource_cls not in (Project, Sample, Library):
        raise ValueError(
            f"Unsupported resource_cls for filter_original_files_by_resource: {resource_cls}"
        )

    def filter_original_files_by_resource(*args, **kwargs):
        # Run the real classmethod with the original args (*args, **kwargs) to ensure whatever
        # arguments the command originally passed (bucket_objects, bucket, sync_timestamp) are used.
        original_files, lockfiles = non_patched_get_syncable_files(*args, **kwargs)

        if resource_cls == Project:
            project_ids = set(resource_ids)
            filtered_original_files = [
                of for of in original_files if of.project_id is None or of.project_id in project_ids
            ]
            filtered_lockfiles = [lf for lf in lockfiles if lf.project_id in project_ids]
            return filtered_original_files, filtered_lockfiles

        if resource_cls == Sample:
            sample_ids = set(resource_ids)
            # Project-level files and lockfiles always pass through.
            # Only sample-level files are narrowed, directly against the requested sample ids.
            filtered_original_files = [
                of
                for of in original_files
                if not of.sample_ids or any(sid in sample_ids for sid in of.sample_ids)
            ]
            return filtered_original_files, lockfiles

        # resource_cls == Library
        library_ids = set(resource_ids)
        # Resolve which samples the requested libraries belong to from the library-level files
        # themselves, same reasoning as Sample's own-tier matching above, just one level deeper -
        # this can only ever narrow sample-level files, never project-level ones.
        library_files = [of for of in original_files if of.library_id in library_ids]
        sample_ids = {sid for of in library_files for sid in of.sample_ids}

        filtered_original_files = [
            of
            for of in original_files
            if of.project_id is None
            or (not of.sample_ids and not of.library_id)
            or (
                not of.library_id
                and of.sample_ids
                and any(sid in sample_ids for sid in of.sample_ids)
            )
            or (of.library_id and of.library_id in library_ids)
        ]
        return filtered_original_files, lockfiles

    return filter_original_files_by_resource


def filter_metadata_by_resource_wrapper(
    resource_cls: type,
    resource_ids: List[str],
    *,
    bulk: bool = False,
    add_new_metadata: Dict | None = None,
    modified_resource_id: str | None = None,
    mutated_field: str | None = None,
    mutated_value: str | None = None,
):
    """
    Build a side_effect for patching the metadata_parser function resource_cls's sync_model/
    sync_metadata reads from, generic across Project, Sample and Library. The caller only ever
    passes the class and resource_ids (plus bulk for Library) - never a metadata_parser function or
    id key directly. Returns a replacement that delegates to the real implementation, then narrows
    the resulting list of metadata dicts down to the ones whose SCPCA_RESOURCE_METADATA_ID_KEY is
    in resource_ids - that's all any of these sources ever need, regardless of which resource or
    source function the list came from.

    Project and Sample each have a single metadata source. Library has two independent ones (one
    metadata.json per regular library, and one project level bulk tsv shared by every project's
    bulk library) - bulk picks between them, so scoping Library still means two separate calls to
    this function (once with bulk=False, once with bulk=True), each still returning the same shape
    as every other call: a single side_effect function, never a dict of them. add_new_metadata/
    modified_resource_id are expected to only ever be passed for the regular (bulk=False) library
    source, matching the real pipeline where only regular libraries are ever newly added or mutated
    in these tests.
    """
    if resource_cls not in (Project, Sample, Library):
        raise ValueError(
            f"Unsupported resource_cls for filter_metadata_by_resource: {resource_cls}"
        )

    id_key = resource_cls.SCPCA_RESOURCE_METADATA_ID_KEY

    def filter_metadata(*args, **kwargs):
        if resource_cls == Project:
            non_patched_metadata_fn = non_patched_load_all_projects_metadata
        elif resource_cls == Sample:
            non_patched_metadata_fn = non_patched_load_all_samples_metadata
        elif bulk:
            non_patched_metadata_fn = non_patched_load_all_bulk_libraries_metadata
        else:
            non_patched_metadata_fn = non_patched_load_all_libraries_metadata

        # Run the real function with the original args (*args, **kwargs) to ensure whatever
        # arguments the caller originally passed are used.
        metadata = non_patched_metadata_fn(*args, **kwargs)
        filtered_metadata = [md for md in metadata if md[id_key] in resource_ids]

        if add_new_metadata:
            filtered_metadata.append(add_new_metadata)

        if modified_resource_id and mutated_field:
            modified_metadata = next(
                (md for md in filtered_metadata if md[id_key] == modified_resource_id), None
            )
            if modified_metadata:
                modified_metadata[mutated_field] = mutated_value

        return filtered_metadata

    return filter_metadata


class TestLoadableResourceABCUtils(TestCase):
    """
    Exercises the two wrapper builders above in isolation, with OriginalFile.get_syncable_files
    and the metadata_parser load_all_* functions mocked out entirely (via return_value, not
    side_effect), so these tests only ever check the wrappers' own filtering logic against fixed
    inputs - no real S3 bucket or metadata file is ever touched here.
    """

    # FILTER_ORIGINAL_FILES_BY_RESOURCE TESTS
    def test_filter_original_files_by_resource_project(self):
        portal_file = OriginalFile(project_id=None)
        project_a_file = OriginalFile(project_id="SCPCP1")
        project_b_file = OriginalFile(project_id="SCPCP2")
        lockfile_a = OriginalFile(project_id="SCPCP1", is_lockfile=True)
        lockfile_b = OriginalFile(project_id="SCPCP2", is_lockfile=True)

        with patch(
            f"{__name__}.non_patched_get_syncable_files",
            return_value=(
                [portal_file, project_a_file, project_b_file],
                [lockfile_a, lockfile_b],
            ),
        ):
            side_effect = filter_original_files_by_resource_wrapper(Project, ["SCPCP1"])
            filtered_original_files, filtered_lockfiles = side_effect()

        self.assertCountEqual(filtered_original_files, [portal_file, project_a_file])
        self.assertCountEqual(filtered_lockfiles, [lockfile_a])

    def test_filter_original_files_by_resource_sample(self):
        portal_file = OriginalFile(project_id=None)
        # Project level file, e.g. samples_metadata.csv - no sample_ids of its own.
        project_level_file = OriginalFile(project_id="SCPCP1", sample_ids=[])
        in_scope_sample_file = OriginalFile(project_id="SCPCP1", sample_ids=["SCPCS1"])
        # Same project as the requested sample, but a different sample - out of scope.
        out_of_scope_sample_file = OriginalFile(project_id="SCPCP1", sample_ids=["SCPCS2"])
        # Multiplexed library file naming more than one sample - in scope if any id matches.
        multiplexed_file = OriginalFile(project_id="SCPCP1", sample_ids=["SCPCS1", "SCPCS3"])
        # A second, uninvolved project - its project level file and lockfile are still kept,
        # since project-level files are never narrowed for Sample requests.
        other_project_level_file = OriginalFile(project_id="SCPCP2", sample_ids=[])
        other_project_sample_file = OriginalFile(project_id="SCPCP2", sample_ids=["SCPCS4"])
        lockfile_a = OriginalFile(project_id="SCPCP1", is_lockfile=True)
        lockfile_b = OriginalFile(project_id="SCPCP2", is_lockfile=True)

        with patch(
            f"{__name__}.non_patched_get_syncable_files",
            return_value=(
                [
                    portal_file,
                    project_level_file,
                    in_scope_sample_file,
                    out_of_scope_sample_file,
                    multiplexed_file,
                    other_project_level_file,
                    other_project_sample_file,
                ],
                [lockfile_a, lockfile_b],
            ),
        ):
            side_effect = filter_original_files_by_resource_wrapper(Sample, ["SCPCS1"])
            filtered_original_files, filtered_lockfiles = side_effect()

        self.assertCountEqual(
            filtered_original_files,
            [
                portal_file,
                project_level_file,
                in_scope_sample_file,
                multiplexed_file,
                other_project_level_file,
            ],
        )
        self.assertCountEqual(filtered_lockfiles, [lockfile_a, lockfile_b])

    def test_filter_original_files_by_resource_library(self):
        portal_file = OriginalFile(project_id=None, library_id=None)
        # Project level file for the requested library's own project.
        project_level_file = OriginalFile(project_id="SCPCP1", sample_ids=[], library_id=None)
        # Sample level file with no library_id of its own, for the requested library's own sample.
        in_scope_sample_level_file = OriginalFile(
            project_id="SCPCP1", sample_ids=["SCPCS1"], library_id=None
        )
        # Same project, different sample, not associated with the requested library - out of scope.
        out_of_scope_sample_level_file = OriginalFile(
            project_id="SCPCP1", sample_ids=["SCPCS2"], library_id=None
        )
        in_scope_library_file = OriginalFile(
            project_id="SCPCP1", sample_ids=["SCPCS1"], library_id="SCPCL1"
        )
        out_of_scope_library_file = OriginalFile(
            project_id="SCPCP1", sample_ids=["SCPCS2"], library_id="SCPCL2"
        )
        # A second, uninvolved project - its project level file and lockfile are still kept,
        # since project-level files are never narrowed for Library requests.
        other_project_level_file = OriginalFile(project_id="SCPCP2", sample_ids=[], library_id=None)
        lockfile_a = OriginalFile(project_id="SCPCP1", is_lockfile=True)
        lockfile_b = OriginalFile(project_id="SCPCP2", is_lockfile=True)

        with patch(
            f"{__name__}.non_patched_get_syncable_files",
            return_value=(
                [
                    portal_file,
                    project_level_file,
                    in_scope_sample_level_file,
                    out_of_scope_sample_level_file,
                    in_scope_library_file,
                    out_of_scope_library_file,
                    other_project_level_file,
                ],
                [lockfile_a, lockfile_b],
            ),
        ):
            side_effect = filter_original_files_by_resource_wrapper(Library, ["SCPCL1"])
            filtered_original_files, filtered_lockfiles = side_effect()

        self.assertCountEqual(
            filtered_original_files,
            [
                portal_file,
                project_level_file,
                in_scope_sample_level_file,
                in_scope_library_file,
                other_project_level_file,
            ],
        )
        self.assertCountEqual(filtered_lockfiles, [lockfile_a, lockfile_b])

    def test_filter_original_files_by_resource_library_bulk_library(self):
        # A bulk library has no OriginalFile tagged with its own library_id at all (it's parsed
        # from a project level bulk tsv instead), so no fixture file
        # here has library_id="SCPCL_BULK". This proves that requesting one doesn't error, and
        # still lets every project/portal level file (and lockfile) - including the bulk tsv file
        # itself, which is project level - pass through, even though nothing can be resolved from
        # the (nonexistent) library-level file.
        portal_file = OriginalFile(project_id=None)
        bulk_tsv_file = OriginalFile(project_id="SCPCP1", sample_ids=[], is_bulk=True)
        unrelated_sample_level_file = OriginalFile(project_id="SCPCP1", sample_ids=["SCPCS1"])
        lockfile = OriginalFile(project_id="SCPCP1", is_lockfile=True)

        with patch(
            f"{__name__}.non_patched_get_syncable_files",
            return_value=(
                [portal_file, bulk_tsv_file, unrelated_sample_level_file],
                [lockfile],
            ),
        ):
            side_effect = filter_original_files_by_resource_wrapper(Library, ["SCPCL_BULK"])
            filtered_original_files, filtered_lockfiles = side_effect()

        # unrelated_sample_level_file is excluded: sample-level files are still scoped down to the
        # requested library's own samples, and a bulk library resolves none (it has no file).
        self.assertCountEqual(filtered_original_files, [portal_file, bulk_tsv_file])
        self.assertCountEqual(filtered_lockfiles, [lockfile])

    def test_filter_original_files_by_resource_unsupported_resource_cls(self):
        with self.assertRaises(ValueError):
            filter_original_files_by_resource_wrapper(OriginalFile, [])

    # FILTER_METADATA_BY_RESOURCE TESTS
    def test_filter_metadata_by_resource_project(self):
        projects_metadata = [
            {"scpca_project_id": "SCPCP1", "title": "Project One"},
            {"scpca_project_id": "SCPCP2", "title": "Project Two"},
        ]

        with patch(
            f"{__name__}.non_patched_load_all_projects_metadata", return_value=projects_metadata
        ):
            side_effect = filter_metadata_by_resource_wrapper(Project, ["SCPCP1"])
            filtered_metadata = side_effect()

        self.assertEqual(filtered_metadata, [projects_metadata[0]])

    def test_filter_metadata_by_resource_project_add_new_and_modify(self):
        projects_metadata = [{"scpca_project_id": "SCPCP1", "title": "Project One"}]
        new_project_metadata = {"scpca_project_id": "SCPCP3", "title": "Project Three"}

        with patch(
            f"{__name__}.non_patched_load_all_projects_metadata", return_value=projects_metadata
        ):
            side_effect = filter_metadata_by_resource_wrapper(
                Project,
                ["SCPCP1"],
                add_new_metadata=new_project_metadata,
                modified_resource_id="SCPCP1",
                mutated_field="title",
                mutated_value="Mutated title",
            )
            filtered_metadata = side_effect()

        self.assertEqual(
            filtered_metadata,
            [{"scpca_project_id": "SCPCP1", "title": "Mutated title"}, new_project_metadata],
        )

    def test_filter_metadata_by_resource_sample(self):
        samples_metadata = [
            {"scpca_sample_id": "SCPCS1", "diagnosis": "Diagnosis One"},
            {"scpca_sample_id": "SCPCS2", "diagnosis": "Diagnosis Two"},
        ]

        with patch(
            f"{__name__}.non_patched_load_all_samples_metadata", return_value=samples_metadata
        ):
            side_effect = filter_metadata_by_resource_wrapper(Sample, ["SCPCS2"])
            filtered_metadata = side_effect()

        self.assertEqual(filtered_metadata, [samples_metadata[1]])

    def test_filter_metadata_by_resource_library_regular_source(self):
        libraries_metadata = [
            {"scpca_library_id": "SCPCL1", "seq_unit": "cell"},
            {"scpca_library_id": "SCPCL2", "seq_unit": "nucleus"},
        ]

        with patch(
            f"{__name__}.non_patched_load_all_libraries_metadata", return_value=libraries_metadata
        ):
            side_effect = filter_metadata_by_resource_wrapper(Library, ["SCPCL1"], bulk=False)
            filtered_metadata = side_effect()

        self.assertEqual(filtered_metadata, [libraries_metadata[0]])

    def test_filter_metadata_by_resource_library_bulk_source(self):
        bulk_libraries_metadata = [
            {"scpca_library_id": "SCPCL3"},
            {"scpca_library_id": "SCPCL4"},
        ]

        with patch(
            f"{__name__}.non_patched_load_all_bulk_libraries_metadata",
            return_value=bulk_libraries_metadata,
        ):
            side_effect = filter_metadata_by_resource_wrapper(Library, ["SCPCL3"], bulk=True)
            filtered_metadata = side_effect()

        self.assertEqual(filtered_metadata, [bulk_libraries_metadata[0]])

    def test_filter_metadata_by_resource_unsupported_resource_cls(self):
        with self.assertRaises(ValueError):
            filter_metadata_by_resource_wrapper(OriginalFile, [])
