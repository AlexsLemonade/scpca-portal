export default {
  computed_file: {
    project: 3,
    sample: null,
    id: 2,
    type: 'PROJECT_ZIP',
    s3_bucket: 'scpca-local-data',
    s3_key: 'dyer_chen_project.zip',
    size_in_bytes: 7183834,
    created_at: '2021-09-10T20:02:07.401145Z',
    updated_at: '2021-09-10T20:02:07.401179Z'
  },
  samples: [
    {
      computed_file: 1,
      project: 3,
      id: 1,
      has_cite_seq_data: false,
      scpca_sample_id: 'SCPCS000109',
      technologies: '10Xv3',
      diagnosis: 'Neuroblastoma',
      subdiagnosis: 'MYCN non-amplified',
      age_at_diagnosis: '9',
      sex: 'F',
      disease_timing: 'Initial Diagnosis',
      tissue_location: 'Adrenal Gland',
      treatment: 'treated',
      seq_units: 'cell',
      additional_metadata: {
        'COG Risk': 'High',
        Treatment: 'treated',
        'IGSS Stage': '4',
        'Primary Site': 'Adrenal'
      },
      created_at: '2021-09-10T20:02:07.315349Z',
      updated_at: '2021-09-10T20:02:07.315377Z'
    }
  ],
  summaries: [
    {
      diagnosis: 'Neuroblastoma',
      seq_unit: 'cell',
      technology: '10Xv3',
      sample_count: 1,
      updated_at: '2021-09-10T20:02:07.360550Z'
    }
  ],
  id: 3,
  pi_name: 'dyer_chen',
  title:
    'Profiling the transcriptional heterogeneity of diverse pediatric solid tumors',
  abstract: '',
  contact: '',
  has_bulk_rna_seq: false,
  has_cite_seq_data: false,
  has_spatial_data: false,
  modalities: '',
  disease_timings: 'Initial Diagnosis',
  diagnoses: 'Neuroblastoma',
  diagnoses_counts: "{'Neuroblastoma'} (1)",
  seq_units: 'cell',
  technologies: '10Xv3',
  sample_count: 1,
  created_at: '2021-09-10T20:02:07.056461Z',
  updated_at: '2021-09-10T20:02:07.403030Z'
}
