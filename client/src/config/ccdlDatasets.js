import { config } from 'config'

export const genericPortalWideDocsLink = {
  learnMore: {
    label: 'here',
    text: 'Please learn more about the portal-wide downloads here.',
    url: config.links.whatPortalWide
  }
}

export const modalityNames = {
  SINGLE_CELL: 'Single-cell data',
  SPATIAL: 'Spatial data'
}
export const formatNames = {
  SINGLE_CELL_EXPERIMENT: 'SingleCellExperiment (R)',
  ANN_DATA: 'AnnData (Python)'
}

export const portalWideLinks = {
  ALL_METADATA: {
    learnMore: config.links.whatDownloadingPortalWideMetadata
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
    learnMore: config.links.whatDownloadingPortalWide
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: {
    learnMore: config.links.whatDownloadingPortalWide
  },
  SINGLE_CELL_ANN_DATA: {
    learnMore: config.links.whatDownloadingPortalWide
  },
  SINGLE_CELL_ANN_DATA_MERGED: {
    learnMore: config.links.whatDownloadingPortalWide
  },
  SPATIAL_SPATIAL_SPACERANGER: {
    learnMore: config.links.whatDownloadingPortalWideSpatial
  }
}

export const projectLinks = {
  ALL_METADATA: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_ANN_DATA: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_ANN_DATA_MERGED: { learnMore: '#tbd' },
  SPATIAL_SPATIAL_SPACERANGER: {
    learnMore: '#tbd'
  }
}
