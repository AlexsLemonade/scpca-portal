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

    diagnosis = "AML"
    seq_unit = "cell"
    technology = "10Xv2_5prime"

    sample_count = 28


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
