export const keys = {
  abstract: 'Abstract',
  computed_files: 'File',
  disease_timings: 'Disease Timing',
  diagnoses: 'Diagnosis',
  human_readable_pi_name: 'Primary Investigator',
  modalities: 'Modalities',
  pi_name: 'Primary Investigator',
  samples: 'Samples',
  sample_count: 'Sample Count',
  seq_units: 'Seq Units',
  summaries: 'Summaries',
  technologies: 'Technologies',
  title: 'Title',
  has_bulk_rna_seq: 'Bulk RNA-Seq',
  has_multiplexed_data: 'Multiplexed',
  has_cite_seq_data: 'CITE-seq',
  has_spatial_data: 'Spatial',
  has_single_cell: 'Single-cell',
  includes_cell_lines: 'Includes cell lines',
  includes_xenografts: 'Includes xenografts'
}

export const values = {
  BULK_RNA_SEQ: 'Bulk RNA-seq',
  CITE_SEQ: 'CITE-seq',
  SINGLE_CELL: 'Single-cell',
  SPATIAL: 'Spatial',
  MULTIPLEXED: 'Multiplexed',
  ANN_DATA: 'AnnData (Python)',
  SINGLE_CELL_EXPERIMENT: 'SingleCellExperiment (R)',
  SPATIAL_SPACERANGER: 'Spaceranger',
  '.rds': 'SingleCellExperiment (.rds)',
  '.h5ad': 'AnnData (.h5ad)',
  // Kit technology names
  '10Xflex_v1.1_multi': 'GEM-X Flex v1'
}

// Alternate presentation
export const fileKeys = {
  includes_files_bulk: 'Bulk RNA-Seq data',
  includes_files_cite_seq: 'CITE-seq data',
  includes_files_multiplexed: 'Multiplexed single-cell data'
}

export const fileValues = {
  BULK_DATA: 'Bulk RNA-Seq data',
  SINGLE_CELL: 'Single-cell data',
  SPATIAL: 'Spatial data',
  MULTIPLEXED: 'Single-cell Multiplexed data'
}
