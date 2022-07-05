export const downloadOptions = {
  PROJECT_ZIP: {
    header: 'Download Single-cell Data',
    data: 'Single-cell data',
    included: {
      has_bulk_rna_data: 'Bulk RNA-seq data',
      has_cite_seq_data: 'CITE-seq data'
    },
    metadata: 'Project and Sample Metadata'
  },
  PROJECT_SPATIAL_ZIP: {
    header: 'Download Spatial Data',
    data: 'Spatial data',
    included: {},
    metadata: 'Project and Sample Metadata'
  },
  PROJECT_MULTIPLEXED_ZIP: {
    header: 'Download Single-cell Multiplexed Data',
    data: 'Single-cell multiplexed data',
    included: {},
    metadata: 'Project and Sample Metadata',
    info: 'This project contains multiplexed samples.'
  },
  SAMPLE_ZIP: {
    header: 'Download Single-cell Data',
    data: 'Single-cell data',
    included: {
      has_bulk_rna_data: 'Bulk RNA-seq data',
      has_cite_seq_data: 'CITE-seq data'
    },
    metadata: 'Project and Sample Metadata'
  },
  SAMPLE_SPATIAL_ZIP: {
    header: 'Download Spatial Data',
    data: 'Spatial data',
    included: {},
    metadata: 'Project and Sample Metadata'
  },
  SAMPLE_MULTIPLEXED_ZIP: {
    header: 'Download Single-cell Multiplexed Data',
    data: 'Single-cell multiplexed data',
    included: {},
    metadata: 'Project and Sample Metadata'
  }
}
