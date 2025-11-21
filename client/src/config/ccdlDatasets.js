import { config } from 'config'

export const genericPortalWideDocsLink = {
  learnMore: {
    label: 'here',
    text: 'Please learn more about the portal-wide downloads here.',
    url: config.links.whatPortalWide
  }
}

export const portalWideLinks = {
  ALL_METADATA: {
    learnMore: config.links.whatDownloadingPortalWideMetadata
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
    learnMore: config.links.whatDownloadingPortalWideSCE
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: {
    learnMore: config.links.whatDownloadingPortalWideSCEMerged
  },
  SINGLE_CELL_ANN_DATA: {
    learnMore: config.links.whatDownloadingPortalWideAnndata
  },
  SINGLE_CELL_ANN_DATA_MERGED: {
    learnMore: config.links.whatDownloadingPortalWideAnndataMerged
  },
  SPATIAL_SPATIAL_SPACERANGER: {
    learnMore: config.links.whatDownloadingPortalWideSpatial
  }
}

export const projectLinks = {
  ALL_METADATA: {
    learnMore: config.links.whatDownloadingProjectMetadata
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT: {
    learnMore: config.links.whatDownloadingProjectSCE
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED: {
    learnMore: '#tbd'
  },
  SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED: {
    learnMore: config.links.whatDownloadingProjectSCEMerged
  },
  SINGLE_CELL_ANN_DATA: {
    learnMore: config.links.whatDownloadingProjectAnndata
  },
  SINGLE_CELL_ANN_DATA_MERGED: {
    learnMore: config.links.whatDownloadingProjectAnndataMerged
  },
  SPATIAL_SPATIAL_SPACERANGER: {
    learnMore: config.links.whatDownloadingProjectSpatial
  }
}
