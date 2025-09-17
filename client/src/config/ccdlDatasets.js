import { config } from 'config'

export const portalWideDatasets = {
  ALL_METADATA: {
    modalTitle: 'Portal-wide Sample Metadata',
    learnMore: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.whatDownloadingPortalWideMetadata
    }
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
    modalTitle: 'Portal-wide Data as SingleCellExperiment (R)',
    learnMore: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.whatDownloadingPortalWide
    }
  },
  SINGLE_CELL_ANN_DATA: {
    modalTitle: 'Portal-wide Data as AnnData (Python)',
    learnMore: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.whatDownloadingPortalWide
    }
  },
  SPATIAL_SINGLE_CELL_EXPERIMENT: {
    modalTitle: 'Portal-wide Spatial Data',
    learnMore: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.whatDownloadingPortalWideSpatial
    }
  }
}
