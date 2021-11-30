export const readableNames = {
  abstract: 'Abstract',
  pi_name: 'Primary Investigator',
  human_readable_pi_name: 'Primary Investigator',
  computed_file: 'File',
  samples: 'Samples',
  summaries: 'Summaries',
  title: 'Title',
  contact: 'Contact',
  contact_name: 'Contact Name',
  contact_email: 'Contact Email',
  has_bulk_rna_seq: 'Bulk RNA-Seq',
  disease_timings: 'Disease Timing',
  diagnoses: 'Diagnosis',
  seq_units: 'Seq Units',
  technologies: 'Technologies',
  sample_count: 'Sample Count',
  modalities: 'Modalities'
}

export const getReadable = (key) => readableNames[key] || key

export default getReadable
