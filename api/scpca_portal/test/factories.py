import factory


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

    type = "FILTERED_COUNTS"
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
    title = "Single-Cell Profiling of Acute Myeloid Leukemia for High-Resolution Chemo-immunotherapy Target Discovery"
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
    contact_name = "Gawad"
    contact_email = "gawad@example.com"
    disease_timings = "Diagnosis, Relapse/Diagnosis at LPCH, Relapsed, Healthy control"
    diagnoses = "AML, Normal"
    diagnoses_counts = "AML (20), Normal (40)"
    seq_units = "cell"
    technologies = "10Xv2_5prime, CITE-seq"
    has_bulk_rna_seq = True

    sample_count = 60


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Sample"

    scpca_id = factory.Sequence(lambda n: "SCPCS0000%d" % n)
    has_cite_seq_data = True
    technologies = "10Xv3"
    diagnosis = "pilocytic astrocytoma"
    subdiagnosis = "NA"
    age_at_diagnosis = "4"
    sex = "M"
    disease_timing = "primary diagnosis"
    tissue_location = "posterior fossa"
    seq_units = "cell"
    cell_count = 42
    additional_metadata = {
        "has_spinal_leptomeningeal_mets": False,
        "braf_status": "Not tested for BRAF status",
    }

    project = factory.SubFactory(LeafProjectFactory)
    computed_file = factory.SubFactory(LeafComputedFileFactory)


class ComputedFileFactory(LeafComputedFileFactory):
    sample = factory.SubFactory(SampleFactory)


class ProjectFactory(LeafProjectFactory):
    sample1 = factory.RelatedFactory(SampleFactory, "project")
    computed_file = factory.SubFactory(LeafComputedFileFactory)
    summary1 = factory.RelatedFactory(ProjectSummaryFactory, factory_related_name="project")
