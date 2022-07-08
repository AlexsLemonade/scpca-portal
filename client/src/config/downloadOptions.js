import { config } from 'config'

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
    data: 'Single-cell data',
    included: {
      has_bulk_rna_data: 'Bulk RNA-seq data',
      has_multiplexed_data: 'Single-cell multiplexed data'
    },
    metadata: 'Project and Sample Metadata',
    info: {
      message: {},
      warning_text: {
        link: {
          label: 'Learn more',
          url: config.links.what_downloading_mulitplexed
        },
        text: 'This project contains multiplexed samples.'
      }
    }
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
    button_label: 'Download',
    data: 'Single-cell multiplexed data',
    included: {},
    metadata: 'Project and Sample Metadata',
    info: {
      message: {
        text_only: 'This is a multiplexed sample.',
        multiplexed_with: {
          text: 'It has been multiplexed with the followig samples.'
        },
        learn_more: {
          label: 'here',
          text: 'Learn more about multiplexed samples ',
          url: config.links.what_downloading_mulitplexed
        }
      },
      warning_text: {
        text: 'If you are planning to work with more than one multiplexed sample, we reccommend downloading the entire project.'
      }
    }
  }
}
