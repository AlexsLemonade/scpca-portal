import factory

from scpca_portal.enums import FileFormats
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

    scpca_id = factory.Sequence(lambda n: f"SCPCP{str(n).zfill(6)}")
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
    additional_restrictions = "Research or academic purposes only"
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

    age = "4"
    age_timing = "diagnosis"
    computed_file1 = factory.RelatedFactory(SampleComputedFileFactory, "sample")
    diagnosis = "pilocytic astrocytoma"
    disease_timing = "primary diagnosis"
    has_cite_seq_data = True
    metadata = factory.LazyFunction(
        lambda: {
            "age": 4,
            "age_timing": "diagnosis",
            "development_stage_ontology_term_id": "NA",
            "diagnosis": "pilocytic astrocytoma",
            "disease_ontology_term_id": "NA",
            "disease_timing": "primary diagnosis",
            "is_cell_line": False,
            "is_xenograft": False,
            "organisms": "Homo sapiens",
            "organisms_ontology_id": "NA",
            "participant_id": "NA",
            "scpca_project_id": "",
            "scpca_sample_id": "",
            "self_reported_ethnicity_ontology_term_id": "NA",
            "sex": "M",
            "subdiagnosis": "NA",
            "submitter": "scpca",
            "submitter_id": "NA",
            "tissue_location": "posterior fossa",
            "tissue_ontology_term_id": "NA",
        }
    )
    multiplexed_with = ["SCPCS000000"]
    project = factory.SubFactory(LeafProjectFactory)
    sample_cell_count_estimate = 42
    scpca_id = factory.Sequence(lambda n: f"SCPCS{str(n).zfill(6)}")
    seq_units = "cell"
    sex = "M"
    subdiagnosis = "NA"
    technologies = "10Xv3"
    tissue_location = "posterior fossa"


class LibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "scpca_portal.Library"

    data_file_paths = [
        factory.Sequence(
            lambda n: f"SCPCP{str(n).zfill(6)}/SCPCS{str(n).zfill(6)}/SCPCL{str(n).zfill(6)}"
        )
    ]
    formats = [FileFormats.SINGLE_CELL_EXPERIMENT]
    is_multiplexed = False
    modality = Library.Modalities.SINGLE_CELL
    project = factory.SubFactory(LeafProjectFactory)
    scpca_id = factory.Sequence(lambda n: f"SCPCL{str(n).zfill(6)}")
    workflow_version = "development"
    # With factory_body, factory instances share attributes by default
    # Use LazyFunction to populate metadata dict so that changes don't propogate to all instances
    metadata = factory.LazyAttribute(
        lambda library_obj: {
            "scpca_library_id": library_obj.scpca_id,
            "scpca_sample_id": "SCPCS000000",
            "technology": "10Xv3",
            "seq_unit": "cell",
            "is_multiplexed": False,
            "has_citeseq": False,
            "has_cellhash": False,
            "processed_cells": 2633,
            "filtered_cells": 3424,
            "unfiltered_cells": 61980,
            "droplet_filtering_method": "emptyDropsCellRanger",
            "total_reads": 121894873,
            "mapped_reads": 90729577,
            "genome_assembly": "Homo_sapiens.GRCh38.104",
            "mapping_index": "Homo_sapiens.GRCh38.104.spliced_intron.txome",
            "transcript_type": "total;spliced",
            "cell_filtering_method": "miQC",
            "normalization_method": "deconvolution",
            "min_gene_cutoff": 200,
            "prob_compromised_cutoff": 0.75,
            "date_processed": "2024-09-10T17:11:52+0000",
            "salmon_version": "1.9.0",
            "alevin_fry_version": "0.7.0",
            "workflow": "https://github.com/AlexsLemonade/scpca-nf",
            "workflow_version": "development",
            "workflow_commit": "319b074caf152f68e6f0bac58af5bcf4481eba2d",
        }
    )


class ProjectFactory(LeafProjectFactory):
    computed_file = factory.RelatedFactory(ProjectComputedFileFactory, "project")
    sample = factory.RelatedFactory(SampleFactory, "project")
    library = factory.RelatedFactory(LibraryFactory, "project")
    summary = factory.RelatedFactory(ProjectSummaryFactory, factory_related_name="project")

    @factory.post_generation
    def add_sample_library_relation(self, create, extracted, **kwargs):
        """
        In order for objects to be associated with eachother via a ManyToMany relationship,
        both objects must first be created.
        This method makes the sample and library association after their creation above.
        """
        if not create:
            return

        sample = self.samples.first()
        library = self.libraries.first()

        sample.libraries.add(library)
