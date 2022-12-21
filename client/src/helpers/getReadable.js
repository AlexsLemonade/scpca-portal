export const readableNames = {
  abstract: 'Abstract',
  computed_files: 'File',
  disease_timings: 'Disease Timing',
  diagnoses: 'Diagnosis',
  has_bulk_rna_seq: 'Bulk RNA-Seq',
  has_multiplexed_data: 'Multiplexed',
  human_readable_pi_name: 'Primary Investigator',
  modalities: 'Modalities',
  pi_name: 'Primary Investigator',
  samples: 'Samples',
  sample_count: 'Sample Count',
  seq_units: 'Seq Units',
  summaries: 'Summaries',
  technologies: 'Technologies',
  title: 'Title'
}

export const getReadable = (key) => readableNames[key] || key

export default getReadable
