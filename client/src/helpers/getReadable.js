export const readableNames = {
  abstract: 'Abstract',
  computed_files: 'File',
  disease_timings: 'Disease Timing',
  diagnoses: 'Diagnosis',
  has_bulk_rna_seq: 'Bulk RNA-Seq',
  has_multiplexed_data: 'Multiplexed',
  has_cite_seq_data: 'CITE-seq',
  has_spatial_data: 'Spatial',
  has_single_cell: 'Single-cell',
  human_readable_pi_name: 'Primary Investigator',
  modalities: 'Modalities',
  pi_name: 'Primary Investigator',
  samples: 'Samples',
  sample_count: 'Sample Count',
  seq_units: 'Seq Units',
  summaries: 'Summaries',
  technologies: 'Technologies',
  title: 'Title',
  SINGLE_CELL: 'Single-cell',
  SPATIAL: 'Spatial',
  MULTIPLEXED: 'Multiplexed',
  ANN_DATA: 'AnnData (Python)',
  SINGLE_CELL_EXPERIMENT: 'SingleCellExperiment (R)'
}

// Alternate presentation
const readableFiles = {
  SINGLE_CELL: 'Single-cell data',
  SPATIAL: 'Spatial data',
  MULTIPLEXED: 'Single-cell Multiplexed data',
  has_cite_seq_data: 'CITE-seq data',
  has_spatial_data: 'Spatial',
  has_single_cell: 'Single-cell',
  has_bulk_rna_seq: 'Bulk RNA-Seq data'
}

export const getReadable = (key) => readableNames[key] || key

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

export default getReadable
