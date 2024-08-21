import factory

from scpca_portal.models import ComputedFile, Library


class ProjectSummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.ProjectSummary"

    diagnosis = "AML"
    seq_unit = "cell"
    technology = "10Xv2_5prime"

    sample_count = 28


class LeafComputedFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.ComputedFile"

    s3_bucket = "scpca-portal-local"
    s3_key = "SCPCR000126/filtered.rds"
    workflow_version = "1.0.0"
    size_in_bytes = 100


class LeafProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Project"

    scpca_id = factory.Sequence(lambda n: "SCPCS0000%d" % n)
    pi_name = "gawad"
    human_readable_pi_name = "Gawad"
    title = (
        "Single-Cell Profiling of Acute Myeloid Leukemia for "
        "High-Resolution Chemo-immunotherapy Target Discovery"
    )
    abstract = """Despite enormous efforts to find better treatments
    for children with acute myeloid leukemia (AML), it remains one of
    the most difficult to treat pediatric cancers. The children that
    are fortunate enough to survive the intense treatment regimens
    suffer both short-term and lifelong side effects of their
    treatments. A major cause of the challenges in treating AML is the
    differences between cells present within leukemia that have varied
    responses to a given treatment. This study will utilize recently
    developed technologies that are able to analyze AML samples one
    cell at a time, providing insights into the disease at the
    cellular level. We produce this higher-resolution understanding of
    the disease using these new technologies and will make our data
    immediately accessible to the research community, with the aim of
    accelerating our efforts to find new ways to cure all children
    with AML"""
    disease_timings = "Diagnosis, Relapse/Diagnosis at LPCH, Relapsed, Healthy control"
    diagnoses = "AML, Normal"
    diagnoses_counts = "AML (20), Normal (40)"
    seq_units = "cell"
    technologies = "10Xv2_5prime, CITE-seq"
    has_bulk_rna_seq = True
    modalities = ["CITE-seq"]
    organisms = ["Homo sapiens"]
    sample_count = 60


class ProjectComputedFileFactory(LeafComputedFileFactory):
    format = ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT
    modality = ComputedFile.OutputFileModalities.SINGLE_CELL


class SampleComputedFileFactory(LeafComputedFileFactory):
    format = ComputedFile.OutputFileFormats.SINGLE_CELL_EXPERIMENT
    modality = ComputedFile.OutputFileModalities.SINGLE_CELL


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Sample"

    additional_metadata = {
        "braf_status": "Not tested for BRAF status",
        "has_spinal_leptomeningeal_mets": False,
    }
    age = "4"
    age_timing = "diagnosis"
    computed_file1 = factory.RelatedFactory(SampleComputedFileFactory, "sample")
    diagnosis = "pilocytic astrocytoma"
    disease_timing = "primary diagnosis"
    has_cite_seq_data = True
    multiplexed_with = ["SCPCP000000"]
    project = factory.SubFactory(LeafProjectFactory)
    sample_cell_count_estimate = 42
    scpca_id = factory.Sequence(lambda n: "SCPCS0000%d" % n)
    seq_units = "cell"
    sex = "M"
    subdiagnosis = "NA"
    technologies = "10Xv3"
    tissue_location = "posterior fossa"


class LibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Library"

    data_file_paths = [factory.Sequence(lambda n: f"SCPCP0000{n}/SCPCS0000{n}/SCPCL0000{n}")]
    formats = [Library.FileFormats.SINGLE_CELL_EXPERIMENT]
    is_multiplexed = False
    modality = Library.Modalities.SINGLE_CELL
    project = factory.SubFactory(LeafProjectFactory)
    scpca_id = factory.Sequence(lambda n: "SCPCL0000%d" % n)
    workflow_version = "development"
    # With factory_body, factory instances share attributes by default
    # Use LazyFunction to populate metadata dict so that changes don't propogate to all instances
    metadata = factory.LazyFunction(
        lambda: {
            "technology": "10Xv3.1",
            "seq_unit": "nucleus",
            "is_multiplexed": True,
            "has_citeseq": False,
            "has_cellhash": True,
            "workflow": "https://github.com/AlexsLemonade/scpca-nf",
            "workflow_version": "development",
        }
    )


class ProjectFactory(LeafProjectFactory):
    computed_file1 = factory.RelatedFactory(ProjectComputedFileFactory, "project")
    sample1 = factory.RelatedFactory(SampleFactory, "project")
    summary1 = factory.RelatedFactory(ProjectSummaryFactory, factory_related_name="project")
