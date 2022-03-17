export default {
  scpca_id: 'SCPCP00003',
  computed_file: {
    project: 'SCPCP00003',
    sample: null,
    id: 2,
    type: 'PROJECT_ZIP',
    s3_bucket: 'scpca-local-data',
    s3_key: 'SCPCP00003.zip',
    size_in_bytes: 7183873,
    created_at: '2021-09-20T22:05:52.857602Z',
    updated_at: '2021-09-20T22:05:52.857634Z'
  },
  samples: [
    {
      scpca_id: 'SCPCS000109',
      computed_file: {
        project: null,
        sample: 'SCPCS000109',
        id: 1,
        type: 'SAMPLE_ZIP',
        s3_bucket: 'scpca-local-data',
        s3_key: 'SCPCS000109.zip',
        size_in_bytes: 7183777,
        created_at: '2021-09-20T22:05:52.778949Z',
        updated_at: '2021-09-20T22:05:52.778993Z'
      },
      project: 'SCPCP00003',
      has_cite_seq_data: false,
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
      created_at: '2021-09-20T22:05:52.788597Z',
      updated_at: '2021-09-20T22:05:52.788630Z'
    }
  ],
  summaries: [
    {
      diagnosis: 'Neuroblastoma',
      seq_unit: 'cell',
      technology: '10Xv3',
      sample_count: 1,
      updated_at: '2021-09-20T22:05:52.825288Z'
    }
  ],
  pi_name: 'dyer_chen',
  human_readable_pi_name: 'Dyer and Chen',
  additional_metadata_keys: 'Treatment, Primary Site, COG Risk, IGSS Stage',
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
  diagnoses_counts: 'Neuroblastoma (1)',
  seq_units: 'cell',
  technologies: '10Xv3',
  sample_count: 38,
  downloadable_sample_count: 4,
  created_at: '2021-09-20T22:05:52.421147Z',
  updated_at: '2021-09-20T22:05:52.859615Z'
}
