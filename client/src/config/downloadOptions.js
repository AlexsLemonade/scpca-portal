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
      learn_more: {
        label: 'Learn more',
        icon: {
          name: 'Warning',
          color: 'status-warning',
          size: 'medium'
        },
        text: 'This project contains multiplexed samples.',
        link: config.links.what_downloading_mulitplexed
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
      text_only: 'This is a multiplexed sample.',
      sample_list: {
        text: 'It has been multiplexed with the followig samples.'
      },
      learn_more: {
        label: 'here',
        text: 'Learn more about multiplexed samples',
        link: config.links.what_downloading_mulitplexed
      },
      download_project: {
        icon: {
          name: 'Warning',
          color: 'status-warning',
          size: 'medium'
        },
        link: {
          icon: {
            name: 'DownloadFile',
            color: 'brand',
            size: 'medium'
          },
          label: 'Download Project',
          url: '#'
        },
        text: 'If you are planning to work with more than one multiplexed sample, we reccommend downloading the entire project.'
      }
    }
  }
}
