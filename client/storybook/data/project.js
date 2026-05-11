export default {
  abstract:
    'Pediatric brain tumors are now the most common cause of mortality from disease in childhood. Molecular characteristics of pediatric high- and low-grade gliomas (PHGG and PLGG), the most common tumor category overall, are crucial to treatment and outcomes, but the impact of these characteristics and of the variety of cell populations in these tumors is poorly understood. We performed single-cell RNA-sequencing on viably banked single cell samples of high- and low- grade glial tumors from children treated at Children’s Hospital Colorado. These samples are part of ongoing single-cell pediatric brain tumor banking that our group initiated a decade ago. The maturity of this resource, collected over a decade, provides us with the opportunity to perform well-powered outcome association studies. Samples are collected during routine surgery and immediately disaggregated to isolate single cells. These are then viably frozen in DMSO and banked for later use. We have tumors that cover the variety of subtypes in each of these diseases, as well as comprehensive clinical information on these cases, which will allow us to correlate molecular subtypes and research findings with these clinical measures. Here, we perform single-cell RNA-sequencing on 26 samples from patients with PLGG. In PLGG, we will leverage scRNA-Seq analysis to identify lineage specific development and subpopulations within these tumors. We will then evaluate single-cell RNA-sequencing signatures and clinical outcomes of LGG with BRAF WT, KIAA1549:BRAF fusion and BRAFV600E to identify unique drivers of aggressiveness of BRAFV600E tumors. These studies will significantly advance our understanding of disease biology and provide the detailed molecular and functional insights needed to identify new therapeutic targets for these biologically and clinically heterogeneous tumors.',
  additional_metadata_keys:
    'BRAF_status, participant_id, scpca_project_id, spinal_leptomeningeal_mets, submitter, submitter_id',
  computed_files: [
    {
      created_at: '2022-12-20T16:02:26.293532Z',
      id: 1278,
      project: 'SCPCP000002',
      s3_bucket: 'scpca-local-data',
      s3_key: 'SCPCP000002.zip',
      sample: null,
      size_in_bytes: 4015745697,
      type: 'PROJECT_ZIP',
      updated_at: '2022-12-20T16:02:26.293539Z',
      workflow_version: 'v0.4.0'
    }
  ],
  contacts: [
    {
      email: 'jean.mulcahy-levy@childrenscolorado.org',
      name: 'Jean Mulcahy Levy'
    }
  ],
  created_at: '2022-12-20T15:48:44.283166Z',
  diagnoses_counts: {
      Ependymoma: 1,
      Ganglioglioma: 5,
      "Ganglioglioma/ATRT": 1,
      "Low grade glioma": 3,
      "Pilocytic astrocytoma": 16
  },
  diagnoses: ['Ependymoma', 'Ganglioglioma', 'Ganglioglioma/ATRT', 'Low grade glioma', 'Pilocytic astrocytoma'],
  disease_timings: ['Initial diagnosis'],
  downloadable_sample_count: 26,
  external_accessions: [
    {
      accession: 'SRP436316',
      has_raw: true,
      url: 'https://trace.ncbi.nlm.nih.gov/Traces/study/?acc=SRP436316&o=acc_s%3Aa'
    },
    {
      accession: 'SRP436322',
      has_raw: true,
      url: 'https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRP436322&o=acc_s%3Aa'
    },
    {
      accession: 'GSE231858',
      has_raw: false,
      url: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE231858'
    },
    {
      accession: 'GSE231859',
      has_raw: false,
      url: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE231859'
    }
  ],
  has_bulk_rna_seq: true,
  has_cite_seq_data: false,
  has_multiplexed_data: false,
  has_single_cell_data: true,
  has_spatial_data: false,
  modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
  human_readable_pi_name: 'Green/Mulcahy Levy',
  multiplexed_sample_count: 0,
  pi_name: 'green_mulcahy_levy',
  publications: [],
  sample_count: 26,
  samples: [
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: '1799T>A; P. V600E',
        submitter_id: '1216',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '14',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292774Z',
          id: 1255,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000027.zip',
          sample: 'SCPCS000027',
          size_in_bytes: 184350972,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292780Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505189Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Ganglioglioma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: false,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: [],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 2189,
      scpca_id: 'SCPCS000027',
      seq_units: ['cell'],
      sex: 'F',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Medial left temporal lobe',
      treatment: 'GTR/NTR',
      updated_at: '2022-12-20T15:48:44.505202Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'NA',
        submitter_id: '1226',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '5',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292799Z',
          id: 1256,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000028.zip',
          sample: 'SCPCS000028',
          size_in_bytes: 111052672,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292805Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505300Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Low grade glioma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: true,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 2003,
      scpca_id: 'SCPCS000028',
      seq_units: ['cell'],
      sex: 'F',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Left posterior fossa',
      treatment: 'GTR',
      updated_at: '2022-12-20T15:48:44.505315Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'NA',
        submitter_id: '855',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '8',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292825Z',
          id: 1257,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000029.zip',
          sample: 'SCPCS000029',
          size_in_bytes: 58653983,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292831Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505410Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Pilocytic astrocytoma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: true,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 936,
      scpca_id: 'SCPCS000029',
      seq_units: ['cell'],
      sex: 'M',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Supracellar',
      treatment: 'XRT/Carbo/VBL',
      updated_at: '2022-12-20T15:48:44.505424Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'Negative for BRAF V600E, not tested for fusion',
        submitter_id: '927',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '15',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292851Z',
          id: 1258,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000030.zip',
          sample: 'SCPCS000030',
          size_in_bytes: 15471264,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292857Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505564Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Pilocytic astrocytoma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: true,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 2022,
      scpca_id: 'SCPCS000030',
      seq_units: ['cell'],
      sex: 'M',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Thalamus',
      treatment: 'GTR',
      updated_at: '2022-12-20T15:48:44.505580Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'NA',
        submitter_id: '879',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '6',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292876Z',
          id: 1259,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000031.zip',
          sample: 'SCPCS000031',
          size_in_bytes: 60357628,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292882Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505675Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Pilocytic astrocytoma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: false,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 818,
      scpca_id: 'SCPCS000031',
      seq_units: ['cell'],
      sex: 'F',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Posterior fossa',
      treatment: 'GTR',
      updated_at: '2022-12-20T15:48:44.505688Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'NA',
        submitter_id: '957',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '13',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.292902Z',
          id: 1260,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000032.zip',
          sample: 'SCPCS000032',
          size_in_bytes: 122351810,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.292909Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505782Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Pilocytic astrocytoma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: true,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 1799,
      scpca_id: 'SCPCS000032',
      seq_units: ['cell'],
      sex: 'F',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Posterior fossa',
      treatment: 'GTR x 2',
      updated_at: '2022-12-20T15:48:44.505795Z'
    },
    {
      additional_metadata: {
        submitter: 'green_mulcahy_levy',
        BRAF_status: 'BRAF:KIAA fusion',
        submitter_id: '1056',
        participant_id: 'NA',
        scpca_project_id: 'SCPCP000002',
        spinal_leptomeningeal_mets: 'No'
      },
      age: '4',
      age_timing: 'diagnosis',
      computed_files: [
        {
          created_at: '2022-12-20T16:02:26.293004Z',
          id: 1261,
          project: null,
          s3_bucket: 'scpca-local-data',
          s3_key: 'SCPCS000033.zip',
          sample: 'SCPCS000033',
          size_in_bytes: 151265721,
          type: 'SAMPLE_ZIP',
          updated_at: '2022-12-20T16:02:26.293014Z',
          workflow_version: 'v0.4.0'
        }
      ],
      created_at: '2022-12-20T15:48:44.505888Z',
      demux_cell_count_estimate: null,
      diagnosis: 'Pilocytic astrocytoma',
      disease_timing: 'Initial diagnosis',
      has_bulk_rna_seq: true,
      has_cite_seq_data: false,
      has_multiplexed_data: false,
      has_single_cell_data: true,
      has_spatial_data: false,
      modalities: ['SINGLE_CELL', 'BULK_RNA_SEQ'],
      multiplexed_with: [],
      project: 'SCPCP000002',
      sample_cell_count_estimate: 2031,
      scpca_id: 'SCPCS000033',
      seq_units: ['cell'],
      sex: 'F',
      subdiagnosis: 'NA',
      technologies: ['10Xv3'],
      tissue_location: 'Posterior fossa',
      treatment: 'NTR',
      updated_at: '2022-12-20T15:48:44.505899Z'
    }
  ],
  scpca_id: 'SCPCP000002',
  seq_units: ['cell'],
  summaries: [
    {
      diagnosis: 'Pilocytic astrocytoma',
      sample_count: 16,
      seq_unit: 'cell',
      technology: '10Xv3',
      updated_at: '2022-12-20T16:02:26.329987Z'
    },
    {
      diagnosis: 'Ganglioglioma',
      sample_count: 5,
      seq_unit: 'cell',
      technology: '10Xv3',
      updated_at: '2022-12-20T16:02:26.333458Z'
    },
    {
      diagnosis: 'Low grade glioma',
      sample_count: 3,
      seq_unit: 'cell',
      technology: '10Xv3',
      updated_at: '2022-12-20T16:02:26.337124Z'
    },
    {
      diagnosis: 'Ganglioglioma/ATRT',
      sample_count: 1,
      seq_unit: 'cell',
      technology: '10Xv3',
      updated_at: '2022-12-20T16:02:26.340337Z'
    },
    {
      diagnosis: 'Ependymoma',
      sample_count: 1,
      seq_unit: 'cell',
      technology: '10Xv3',
      updated_at: '2022-12-20T16:02:26.343580Z'
    }
  ],
  technologies: ['10Xv3'],
  title: 'Single cell RNA sequencing of pediatric low-grade gliomas',
  unavailable_samples_count: 0,
  updated_at: '2022-12-20T16:02:26.325284Z'
}
