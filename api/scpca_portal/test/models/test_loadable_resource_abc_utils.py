"""
Generic, single-location versions of the filter_original_files_by_* and filter_metadata_by_*
side_effect wrappers duplicated across test_project_loadable_resource.py,
test_sample_loadable_resource.py and test_library_loadable_resource.py. Each wrapper here is
parameterized by resource_cls (Project, Sample or Library) instead of being copy-pasted per model.

filter_original_files_by_resource_wrapper resolves each resource_cls's scope independently -
Project keeps every file (any level) and every lockfile belonging to the given project ids, no
further narrowing, since requesting a project means everything in it.

Sample and Library both narrow only their own tier's files (sample-level / library-level,
respectively, matched directly against the requested ids) - neither narrows project-level files or
lockfiles down to a resolved project. This isn't an oversight: OriginalFile only records literal
files that exist in the bucket, but a resource's real existence is declared by its metadata row, not
by having a file of its own - a bulk sample gets a row in the project's shared samples_metadata.csv
exactly like every regular sample does, and a bulk library gets a row in the project's shared bulk
tsv (see Library.new_load_metadata), yet neither one has any OriginalFile carrying its own id. The
original-files layer exists to support metadata parsing (e.g. ensuring samples_metadata.csv itself
gets synced), not to independently corroborate which resources exist - so trying to resolve "which
project does this sample/library id belong to" from file-level id matching would silently return
nothing for a bulk resource, and the project-level metadata file it's actually declared in would
never get synced as a result. Project-level files and lockfiles are therefore always kept for every
resource_cls, exactly like Project's own "everything in scope" behavior; only each resource_cls's
own tier of files is actually scoped down to the requested ids. A Sample/Library request whose ids
match no file for that tier simply narrows to nothing at that tier - it never falls back to
"every sample" or "every library" the way a plain per-file membership check would.

filter_metadata_by_resource_wrapper takes resource_cls the same way the original files wrapper
does - the caller just passes the class and resource_ids, never a metadata_parser function or id
key directly. Internally it switches on resource_cls to pick which of this file's own
non_patched_load_all_*_metadata functions to delegate to and which SCPCA_RESOURCE_METADATA_ID_KEY
to filter on, since underneath every metadata source is just a list of dicts narrowed down to the
ones whose id key is in resource_ids - one generic filtering body covers all of them once the
right source function is picked. Library is the only resource_cls with two independent metadata
sources (one metadata.json per regular library, and one project level bulk tsv shared by every
project's bulk library); the keyword-only `bulk` flag picks between them, so a caller scoping
Library still makes two separate calls to this same function (once with bulk=False, once with
bulk=True) rather than getting a dict of side_effects back - every call still returns the same
shape: a single side_effect function.

These wrappers aren't wired into the three files above yet - this file only establishes and tests
them in isolation, via TestLoadableResourceABCUtils below.
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
    Build a side_effect for patching OriginalFile.get_syncable_files, generic across Project,
    Sample and Library. Returns a replacement that delegates to the real implementation, then
    narrows the result to the given resource_ids - project ids, sample ids or library ids,
    according to resource_cls. See the module docstring above for how scope is resolved for
    Sample/Library.
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
            # Project-level files (and lockfiles) always pass through - see the module docstring
            # for why a bulk sample makes that necessary, not just permissive. Only sample-level
            # files are actually narrowed, directly against the requested sample ids.
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
        # A second, uninvolved project - its project level file and lockfile are still kept: a
        # bulk sample (see the module docstring) has no file of its own to resolve a project
        # from, so project-level files and lockfiles are never narrowed down for Sample requests.
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

    def test_filter_original_files_by_resource_sample_bulk_sample(self):
        # A bulk sample has no OriginalFile tagged with its own sample_ids at all - it's declared
        # purely by its row in the project's shared samples_metadata.csv (see the module
        # docstring), so no fixture file here has sample_ids=["SCPCS_BULK"]. This proves requesting
        # one doesn't error, and still lets every project/portal level file (and lockfile) -
        # including samples_metadata.csv itself, which is project level - pass through.
        portal_file = OriginalFile(project_id=None)
        samples_metadata_file = OriginalFile(project_id="SCPCP1", sample_ids=[])
        unrelated_sample_file = OriginalFile(project_id="SCPCP1", sample_ids=["SCPCS1"])
        lockfile = OriginalFile(project_id="SCPCP1", is_lockfile=True)

        with patch(
            f"{__name__}.non_patched_get_syncable_files",
            return_value=(
                [portal_file, samples_metadata_file, unrelated_sample_file],
                [lockfile],
            ),
        ):
            side_effect = filter_original_files_by_resource_wrapper(Sample, ["SCPCS_BULK"])
            filtered_original_files, filtered_lockfiles = side_effect()

        # unrelated_sample_file is excluded: sample-level files are still scoped down to the
        # requested sample ids, and a bulk sample resolves none (it has no file).
        self.assertCountEqual(filtered_original_files, [portal_file, samples_metadata_file])
        self.assertCountEqual(filtered_lockfiles, [lockfile])

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
        # A second, uninvolved project - its project level file and lockfile are still kept: a
        # bulk library (see the module docstring) has no file of its own to resolve a project
        # from, so project-level files and lockfiles are never narrowed down for Library requests.
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
        # from a project level bulk tsv instead - see the module docstring), so no fixture file
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
