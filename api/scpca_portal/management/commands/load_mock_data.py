import random
from typing import Dict

from django.conf import settings
from django.core.management.base import BaseCommand

from scpca_portal.config.logging import get_and_configure_logger
from scpca_portal.management.commands.purge_project import purge_project
from scpca_portal.models import ComputedFile, Project, Sample

logger = get_and_configure_logger(__name__)

mock_projects = [
    {
        "scpca_id": "SCPCP00001",
        "pi_name": "david_teachey",
        "human_readable_pi_name": "David Teachey",
        "title": "Single-cell Profiling of Early T-cell Precursor Acute Lymphoblastic Leukemia",
        "abstract": """Early T-cell precursor acute lymphoblastic leukemia (ETP ALL) is a type of T-cell acute lymphoblastic leukemia (T-ALL). Children with ETP ALL and non-ETP T-ALL have a similar chance to be cured. But, children with ETP ALL are more likely than children with non-ETP T-ALL not to respond to therapy. Children with non-ETP T-ALL are more likely to respond to therapy and then have the leukemia come back (relapse) than children with ETP ALL. We do not understand why some children with ETP ALL do not respond to treatment. We also do not understand why children with ETP ALL and non-ETP T-ALL respond differently to therapy. ETP ALL and non-ETP T-ALL are cancers of T-cells. Even though ETP ALL is a T-cell leukemia it shares many features with different types of leukemia such as acute myelogenous leukemia (AML) and T-myeloid mixed-phenotype acute leukemia (TM-MPAL). We need to understand better how ETP is similar to and different from other types of leukemia. This may help us make better treatments.""",
    },
    {
        "scpca_id": "SCPCP00002",
        "pi_name": "alice_sorangi",
        "human_readable_pi_name": "Alice Sorangi",
        "title": "Single-cell Profiling of Pediatric Bone Sarcomas",
        "abstract": """Each year in the U.S., about 1600 children and young adults are diagnosed with sarcoma--tumors affecting bones, muscle or cartilage. The majority of these are bone tumors, which include osteosarcoma (800 children diagnosed each year) and some Ewing sarcomas (250 cases each year). Bone sarcomas are rare, heterogeneous, and not yet fully characterized. Survival rates are in the 60% and as low as 20-30% for metastatic disease, and outcomes have not improved much over the past decade. To find novel effective approaches for sarcoma therapy, we need to better understand it at a single cell and molecular level. Novel techniques now allow us to get a "snapshot" of each and every single cell individually. These snapshots give us detailed information about which genes are expressed in any and every cell. By comparing these gene expression profiles, we can identify cells that are similar or different within the same tumor.""",
    },
    {
        "scpca_id": "SCPCP00003",
        "pi_name": "trevor_pugh",
        "human_readable_pi_name": "Trevor Pugh",
        "title": "Dissecting Pediatric Brain Tumour Progression Using Single-nuclei Sequencing",
        "abstract": """Brain cancer is the most common cancer in children. While treatments with chemotherapy and radiation can be effective initially, brain tumors often come back and are resistant to further treatment. To understand what happens at the cellular level between initial diagnosis and cancer recurrence, we will study these cells at both timepoints. While past research has focused primarily on cancer cells, we will also study the non-cancerous cells that inhabit brain tumors that may contribute ingredients that cancer cells need to grow. By comparing cancerous and non-cancerous cells before and after treatment, we expect to find specific relationships between these cells that allow tumors to regrow after surgery and radiation. By sharing these data with the scientific community through the Single-cell Pediatric Cancer Atlas, we will have greater power to understand cancer/non-cancer cell relationships, compare these to normal relationships between healthy brain cells, and to nominate treatments that can treat or even prevent the return of cancer after initial treatment.""",
    },
    {
        "scpca_id": "SCPCP00004",
        "pi_name": "andrew_murphy",
        "human_readable_pi_name": "Andrew Murphy",
        "title": "Single Nuclear RNA-seq and Spatial Transcriptomic Analysis of Anaplastic and Favorable Histology Wilms Tumor",
        "abstract": """Wilms tumor is the most common pediatric kidney cancer. The best predictor of clinical outcome for Wilms tumor patients is how their tumor looks under the microscope (histology). The majority of Wilms tumor patients have favorable histology tumors that respond to surgery, chemotherapy, and radiation. These tumors are usually called triphasic tumors because they contain three main cell types--epithelial cells, blastemal cells, and stromal cells. A favorable histology Wilms tumor may transition into an unfavorable histology tumor by developing anaplasia (strikingly abnormal cellular divisions seen under the microscope). Unfavorable histology tumors (diffuse anaplasia) account for 5% of Wilms tumor cases but are resistant to treatment and are responsible for 50% of deaths from this disease. Usually, the resistant/anaplastic component of the tumor makes up only a fraction of the total number of cells in the cancer. A critical barrier to understanding therapeutic resistance in this disease is that studies performed to sequence the resistant component is diluted by the other components of the tumor. Therefore, the current proposal aims to use two technologies (single-nuclear-RNA sequencing and spatial transcriptomics) to isolate the gene expression patterns of individual cell types in Wilms tumor and to focus on the anaplastic/resistant cells.""",
    },
    {
        "scpca_id": "SCPCP00005",
        "pi_name": "charles_mullighan",
        "human_readable_pi_name": "Charles Mullighan",
        "title": "Single-cell Profiling of Childhood Acute Lymphoblastic Leukemia",
        "abstract": """This project will perform single-cell analysis of tumor cells and tumor microenvironment cells in 30 cases of acute lymphoblastic leukemia (ALL). The goal is to identify tumor intrinsic and microenvironmental determinants of tumor formation and progression.

        Previous single-cell gene expression and mutational profiling studies of ALL have shown that both the tumor cells and bone marrow non-tumor cells are heterogeneous (variable) in the patterns of gene expression and tumor mutations. For example, tumor mutations can be mapped to subpopulations of cells within a single sample specific, and gene expression signatures in non-tumor cells are associated with disease relapse. In addition, single-cell profiling has shown that ALL tumor cells acquire characteristics associated with treatment resistance when cultured with bone marrow stroma. Single-cell profiling approaches can identify non-tumor T cells that show distinct patterns of activity, and potential reactivity against the tumor cells, highlighting a potential avenue for therapy. However, there are no systematic data using single-cell profiling in carefully selected cohorts of good-risk and high-risk ALL to dissect the relationship of tumor cells and the tumor microenvironment at single-cell resolution. This proposal will perform such a study in a cohort of ALL samples that have detailed characterization of the bulk tumor population, and available xenografts (tumor cells propagated in mice) to enable the data and samples to be useful as a resource for the general research community.""",
    },
    {
        "scpca_id": "SCPCP00006",
        "pi_name": "adam_green",
        "human_readable_pi_name": "Adam Green",
        "title": "Single Cell RNA Sequencing of Pediatric High- and Low-Grade Gliomas",
        "abstract": """Low-grade gliomas (LGG) are the most common brain tumors diagnosed in children, and high-grade gliomas (HGG) are the most common cause of death. While many children can be treated with surgery alone for LGG, a large number of patients are unable to undergo surgery due to the location of the tumor, while others carry higher risk factors due to underlying mutations in the tumor. While low-grade gliomas are often characterized as "benign" tumors, for patients with aggressive tumor markers or a tumor located in critical brain structures, there is significant morbidity and mortality associated with their tumor. A better understanding of these tumors is necessary to identify new treatment methods and ways to identify patients who need an aggressive approach versus patients who may show a more indolent course. For high-grade gliomas, the only proven therapy is radiation, which is not curative, and these patients suffer nearly 100% mortality; improved treatments are desperately needed. We believe a deeper understanding of these tumors through single-cell RNA-Seq will help provide this knowledge leading to new treatment options.""",
    },
    {
        "scpca_id": "SCPCP00007",
        "pi_name": "charles_gawad",
        "human_readable_pi_name": "Charles Gawad",
        "title": "Single-Cell Profiling of Acute Myeloid Leukemia for High-Resolution Chemo-immunotherapy Target Discovery",
        "abstract": """Despite enormous efforts to find better treatments for children with acute myeloid leukemia (AML), it remains one of the most difficult to treat pediatric cancers. The children that are fortunate enough to survive the intense treatment regimens suffer both short-term and lifelong side effects of their treatments. A major cause of the challenges in treating AML is the differences between cells present within leukemia that have varied responses to a given treatment. This study will utilize recently developed technologies that are able to analyze AML samples one cell at a time, providing insights into the disease at the cellular level. We produce this higher-resolution understanding of the disease using these new technologies and will make our data immediately accessible to the research community, with the aim of accelerating our efforts to find new ways to cure all children with AML.""",
    },
    {
        "scpca_id": "SCPCP00008",
        "pi_name": "michael_dyer",
        "human_readable_pi_name": "Michael Dyer",
        "title": "Profiling the Transcriptional Heterogeneity of Diverse Pediatric Solid Tumors",
        "abstract": """Pediatric solid tumors arise during the development of diverse tissues such as bone, muscle and adrenal gland. The tumor cells maintain many features of the normal tissue where they develop including the developmental hierarchy. As a result, cells within an individual patient's tumor has features of different developmental stages. This tumor heterogeneity is important because, in some patients, a subset of those cells survive treatment and contribute to disease relapse which is often fatal. Single-cell profiling is essential to understand the tumor heterogeneity at diagnosis and after treatment and the interactions between tumor cells and normal cells in the tumor microenvironment.""",
    },
    {
        "scpca_id": "SCPCP00009",
        "pi_name": "natalie_collins",
        "human_readable_pi_name": "Natalie Collins",
        "title": "Single-cell Atlas of Pediatric Osteosarcoma",
        "abstract": """Children with metastatic osteosarcoma have an especially poor prognosis. Treatments for osteosarcoma have not changed in decades which highlights the need for new and novel therapies. Little is known about why tumors form metastases in some patients and remain localized in other patients. Cells from the tumor break free and circulate in the bloodstream of patients with osteosarcoma. These cells can be detected as circulating tumor cells (CTCs) and are thought to contribute to metastasis formation. Most tumor studies are undertaken on bulk tumor samples, which can mask subtle variations from cell to cell and don't allow identification of individual cells within the tumor. We believe, by looking at individual cells within a tumor and at CTCs, that we will be able to characterize both cancer cells, immune cells, and CTCs, and how these relate to one another and change from person to person and from disease to disease. We aim to perform single-cell profiling on tumor samples from children with osteosarcoma in order to create the first osteosarcoma tumor atlas.""",
    },
    {
        "scpca_id": "SCPCP00010",
        "pi_name": "brock_chirstensen",
        "human_readable_pi_name": "Brock Christensen",
        "title": "Single-cell Gene Expression and Cytosine Modification Profiling in Pediatric Central Nervous System Tumors",
        "abstract": """Single-cell gene expression profiling of pediatric central nervous system (CNS) tumors holds great potential to further our understanding of carcinogenesis, augment prognostic indicators, and identify rational therapeutic targets. Whereas the genomic characteristics of these tumors are fairly well-defined in aggregate, the extent to which cellular variation is associated with carcinogenesis and clinical outcomes is largely unknown. We will profile single nuclei gene expression in 34 brain tumor specimens from 29 unique individuals with a diagnosis of ependymoma, glioma, or embryonal CNS tumor with substantial follow-up time, as well as nontumor brain tissue from four pediatric controls. We will compare gene expression landscapes between tumor and nontumor control, among tumor types, and compare between tumor variation using five tumors with matched specimens. Pediatric brain tumors are rare and single nucleus expression profiles from such a diverse group of diagnoses has not been studied to our knowledge. We will capture and measure gene expression in 5000 single nuclei and conduct bulk RNA sequencing. Molecular classifications of CNS tumors have identified subgroups which predict response to treatment. In addition, we will compare epigenetic modification profiles collected on these samples with their gene expression profiles to further both cell type deconstruction methods, as well as investigate functional aspects of epigenetic gene regulation. The data and results from this study are expected to reveal an abundance of information about pediatric CNS tumors with value for the broader scientific community.""",
    },
]

mock_sample_options = {
    "diagnosis": [
        "Anaplastic astrocytoma",
        "Anaplastic glioma",
        "Diffuse midline glioma",
        "Ependymoma",
        "Early T-cell precursor T-cell acute lymphoblastic leukemia",
        "Ganglioglioma",
        "Ganglioglioma/ATRT",
        "Glioblastoma",
        "High grade glioma",
        "Low grade glioma",
        "Neuroblastoma",
        "Non-early T-cell precursor T-cell acute lymphoblastic leukemia",
        "Normal margin",
        "Pilocytic astrocytoma",
        "Pleomorphic xanthoastrocytoma",
        "Rhabdomyosarcoma",
        "T-myeloid mixed phenotype acute leukemia",
        "Wilms tumor",
    ],
    "subdiagnosis": [
        "Favorable",
        "Anaplastic",
        "Embryonal rhabdomyosarcoma",
        "Alveolar rhabdomyosarcoma",
        "Spindle cell/sclerosing rhabdomyosarcoma",
        "Supratentorial",
        "Epithelioid/giant cell",
        "Epithelioid",
        "Glioblastoma treatment induced",
        "Gliomatosis cerebri",
        "Poorly differentiated, RIG",
        "NA",
    ],
    "seq_units": ["cell", "nucleus"],
    "technologies": ["10Xv3", "10Xv3.1", "10Xv2_5prime", "10Xv2"],
    "disease_timing": [
        "Initial diagnosis",
        "Metastatic recurrence of anaplastic pleomorphic xanthoastrocytoma",
        "Recurrence",
        "Metastatic (autopsy)",
        "Initial diagnosis (prior needle biopsy)",
    ],
    "tissue_location": [
        "Right thalamus/midbrain",
        "Right thalamus",
        "Left frontal with right frontal and left basal ganglia involvement",
        "Pons/Cerebellum",
        "Left cerebral hemisphere",
        "Left frontal (with satellite lesions in same lobe)",
        "Cerebellum (multiple masses)",
        "Right frontotemporal",
        "Right parietal",
        "NA",
        "Right cerebellum",
        "Left temporal/occipital",
        "Left frontal",
        "Right cerebral hemisphere (centered in right parietal lobe)",
        "C/T-spine",
        "Pons and surrounding areas",
        "Left thalamus",
        "Left temporal",
        "3rd/lateral ventricles, pineal",
        "Right frontal leptomeninges",
        "Posterior fossa",
        "Right superior temporal gyrus",
        "Medial left temporal lobe",
        "Left posterior fossa",
        "Supracellar",
        "Thalamus",
        "Spinal",
        "Right mesial temporal lobe",
        "Thalamic",
        "Basal ganglia",
        "Right precentral gyrus",
        "Right parahippocampus",
        "Cerebellar",
        "Right temporal",
        "Left mesial temporal",
        "Adrenal gland",
        "Mediastinal mass",
        "Retroperitoneal mass",
        "Abdominal mass",
        "Retrohepatic, perivascular mass, IVC",
        "Paraspinal mass",
        "Pelvic mass",
        "Peritoneal mass",
        "Aortocaval mass",
        "Kidney",
        "Liver",
        "Right kidney",
        "Left kidney",
        "Diaphram",
        "Lung",
        "Abdominal wall",
        "Infratemporal fossa",
        "Prostate",
        "Prostate/bladder",
        "Pelvis",
        "Stomach",
        "Thigh",
        "Parapharyngeal",
        "Abdomen/pelvis",
        "Calf",
        "Chest",
        "Omentum",
        "Oropharynx",
        "Retroperitoneum",
        "Peritracheal",
        "Pancreas",
        "Breast",
        "Back soft tissue",
        "Bladder",
    ],
    "treatment": [
        "No treatment",
        "Treated",
        "no treatment",
        "Yes",
        "No",
        "Debulking, RT, irinotecan/cetuximab",
        "GTR, vemurafenib, chloroquine",
        "STR, Carbo/Vbl",
        "Upfront resection",
        "Resection post chemotherapy",
    ],
    "sex": ["M", "F", "NA"],
}

mock_metadata_keys = [
    "primary_site",
    "IGSS_stage",
    "COG_risk",
    "MYCN_status",
    "fusion_status",
    "sample_type",
    "stage",
    "group",
    "risk_stratum",
    "primary_or_metastasis",
    "spinal_leptomeningeal_mets",
    "molecular_characteristics",
    "outcome",
    "BRAF_status",
    "relapse_status",
    "vital_status",
    "metastasis ",
]

mock_sample_index = 0


def get_mock_option(key: str, k=False):
    if k:
        return random.choices(mock_sample_options[key], k=k)
    return random.choice(mock_sample_options[key])


def purge_all_projects():
    for project in Project.objects.all():
        purge_project(project.scpca_id, False)


def mock_package_files_for_project(project: Project,):
    computed_file = ComputedFile(
        type="PROJECT_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=f"{project.scpca_id}.zip",
        size_in_bytes=random.randrange(200, 160000),
    )

    computed_file.save()

    project.computed_file = computed_file
    project.save()

    return computed_file


def mock_package_files_for_sample(sample: Dict,):
    sample_id = sample["scpca_sample_id"]
    zip_file_name = f"{sample_id}.zip"

    computed_file = ComputedFile(
        type="SAMPLE_ZIP",
        workflow_version="0.0.1",
        s3_bucket=settings.AWS_S3_BUCKET_NAME,
        s3_key=zip_file_name,
        size_in_bytes=random.randrange(200, 160000),
    )

    computed_file.save()

    return computed_file


def mock_sample_from_dict(project: Project, sample: dict, computed_file: ComputedFile):
    # First figure out what metadata is additional.
    # This varies project by project, so whatever's not on
    # the Sample model is additional.
    sample_columns = [
        "scpca_sample_id",
        "technologies",
        "diagnosis",
        "subdiagnosis",
        "age_at_diagnosis",
        "sex",
        "disease_timing",
        "tissue_location",
        "treatment",
        "seq_units",
        "has_cite_seq_data",
        "has_spacial_data",
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
        age_at_diagnosis=sample["age_at_diagnosis"],
        sex=sample["sex"],
        disease_timing=sample["disease_timing"],
        tissue_location=sample["tissue_location"],
        treatment=sample["treatment"],
        seq_units=sample["seq_units"],
        cell_count=sample["cell_count"],
        has_cite_seq_data=sample["has_cite_seq_data"],
        has_spatial_data=sample["has_spatial_data"],
        additional_metadata=additional_metadata,
    )
    sample_object.save()

    return sample_object


def mock_samples_for_project(project: Project):

    created_samples = []
    samples_to_mock = range(random.randrange(10, 45))

    # limit variety per project
    mock_technologies = get_mock_option("technologies", k=random.randrange(1, 3))
    mock_diagnosis = get_mock_option("diagnosis", k=random.choice([1, 10, 5]))
    mock_subdiagnosis = get_mock_option("subdiagnosis", k=random.randrange(1, 10, 5))
    mock_seq_units = get_mock_option("seq_units", k=random.randrange(1, 3))

    for _ in samples_to_mock:

        global mock_sample_index
        mock_sample_index += 1
        sample_id = f"SCPCS{mock_sample_index:05d}"

        sample = {
            "scpca_sample_id": sample_id,
            "technologies": random.choice(mock_technologies),
            "diagnosis": random.choice(mock_diagnosis),
            "subdiagnosis": random.choice(mock_subdiagnosis),
            "age_at_diagnosis": round(random.uniform(0.08, 24.0), 1),
            "sex": get_mock_option("sex"),
            "disease_timing": get_mock_option("disease_timing"),
            "tissue_location": get_mock_option("tissue_location"),
            "treatment": get_mock_option("treatment"),
            "seq_units": random.choice(mock_seq_units),
            "cell_count": random.randrange(1, 100),
            "has_cite_seq_data": random.choice([False, True]),
            "has_spatial_data": random.choice([False, True]),
        }

        additional_metadata_keys = random.choices(
            mock_metadata_keys, k=random.randrange(0, len(mock_metadata_keys))
        )

        for k in additional_metadata_keys:
            sample[k] = "Mocked additional metadata"

        computed_file = mock_package_files_for_sample(sample)
        sample_object = mock_sample_from_dict(project, sample, computed_file)

        created_samples.append(sample_object)

    mock_package_files_for_project(project)

    return created_samples


def replace_db_with_mock_data():
    purge_all_projects()

    global mock_projects

    # Make sure we're starting with a blank slate for the zip files.
    for project in mock_projects:

        project.update({"has_bulk_rna_seq": random.choice([True, False])})

        project, created = Project.objects.get_or_create(**project, contact="email@example.com")

        if not created:
            # Only import new projects. If old ones are desired
            # they should be purged and readded.
            continue

        print(f"Mocking data for project {project.scpca_id}")
        created_samples = mock_samples_for_project(project)
        print(f"Created {len(created_samples)} samples for project {project.scpca_id}")


class Command(BaseCommand):
    help = """Empties database and populates the database with mock data."""

    def handle(self, *args, **options):
        replace_db_with_mock_data()
