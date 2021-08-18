import factory


class ProjectSummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.ProjectSummary"

    diagnosis = "AML"
    seq_unit = "cell"
    technology = "10Xv2_5prime"

    sample_count = 28


class LeafProcessorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Processor"

    name = "CellRanger"
    version = "1.0.0"
    workflow_name = "cellranger-quant"


class LeafComputedFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.ComputedFile"

    type = "FILTERED_COUNTS"
    s3_bucket = "scpca-portal-local"
    s3_key = "SCPCR000126/filtered_sce.rds"


class LeafProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Project"

    pi_name = "gawad"
    project_title = "Single-Cell Profiling of Acute Myeloid Leukemia for High-Resolution Chemo-immunotherapy Target Discovery"
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
    project_contact = "gawad"
    disease_timings = "Diagnosis, Relapse/Diagnosis at LPCH, Relapsed, Healthy control"
    diagnoses = "AML, Normal"
    seq_units = "cell"
    technologies = "10Xv2_5prime, CITE-seq"

    sample_count = 60


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Sample"

    has_cite_seq_data = True
    scpca_sample_id = "SCPCS000034"
    technology = "10Xv3"
    diagnosis = "pilocytic astrocytoma"
    subdiagnosis = "NA"
    age_at_diagnosis = "4"
    sex = "M"
    disease_timing = "primary diagnosis"
    has_spinal_leptomeningeal_mets = False
    tissue_location = "posterior fossa"
    braf_status = "Not tested for BRAF status"
    treatment = "STR"
    seq_unit = "cell"

    project = factory.SubFactory(LeafProjectFactory)


class SampleProcessorAssociationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.SampleProcessorAssociation"

    sample = factory.SubFactory(SampleFactory)
    processor = factory.SubFactory(LeafProcessorFactory)


class ComputedFileFactory(LeafComputedFileFactory):

    processor = factory.SubFactory(LeafProcessorFactory)
    sample = factory.SubFactory(SampleFactory)


class ProcessorFactory(LeafProcessorFactory):
    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        sample = SampleFactory()
        self.samples.add(sample)
        self.computed_files.add(ComputedFileFactory(sample=sample, processor=self))


class ProjectFactory(LeafProjectFactory):
    sample1 = factory.RelatedFactory(SampleFactory, "project")
    computed_file1 = factory.RelatedFactory(LeafComputedFileFactory, factory_related_name="project")
    summary1 = factory.RelatedFactory(ProjectSummaryFactory, factory_related_name="project")
