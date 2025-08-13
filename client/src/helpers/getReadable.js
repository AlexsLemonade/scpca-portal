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
  includes_cell_lines: 'Includes cell lines',
  includes_xenografts: 'Includes xenografts',
  modalities: 'Modalities',
  pi_name: 'Primary Investigator',
  samples: 'Samples',
  sample_count: 'Sample Count',
  seq_units: 'Seq Units',
  summaries: 'Summaries',
  technologies: 'Technologies',
  title: 'Title',
  BULK_RNA_SEQ: 'Bulk RNA-seq',
  CITE_SEQ: 'CITE-seq',
  SINGLE_CELL: 'Single-cell',
  SPATIAL: 'Spatial',
  MULTIPLEXED: 'Multiplexed',
  ANN_DATA: 'AnnData (Python)',
  SINGLE_CELL_EXPERIMENT: 'SingleCellExperiment (R)',
  '.rds': 'SingleCellExperiment (.rds)',
  '.h5ad': 'AnnData (.h5ad)',
  spatialFileFormat: 'Sptial format' // TODO: Add SPATIAL file format for DatasetDownloadFileSummary
}

// Alternate presentation
const readableFiles = {
  SINGLE_CELL: 'Single-cell data',
  SPATIAL: 'Spatial data',
  MULTIPLEXED: 'Single-cell Multiplexed data',
  has_cite_seq_data: 'CITE-seq data',
  has_spatial_data: 'Spatial',
  has_single_cell: 'Single-cell',
  has_bulk_rna_seq: 'Bulk RNA-Seq data',
  has_multiplexed_data: 'Multiplexed single-cell data'
}

export const getReadable = (key) => readableNames[key] || key

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

export default getReadable
