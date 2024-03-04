import { config } from 'config'

export const combinedFiles = [
  {
    // This specifies what we present to be combined.
    // Also prevents rendering these values individually when truthy.
    keys: ['modality', 'has_cite_seq_data'],
    // These rules must all be true to apply.
    // Checked via: computedFile[key] === value
    rules: {
      modality: 'SINGLE_CELL',
      has_cite_seq_data: true,
      format: 'SINGLE_CELL_EXPERIMENT'
    }
  }
]

// Specifies which keys need to be resolved
// for downloadable file contents.
export const dynamicKeys = [
  'modality'
]

// This is a list of keys to check for true.
export const dataKeys = [
  'has_bulk_rna_seq',
  'has_cite_seq_data',
]

// This prevents appending "as Single-Cell Experiment" etc.
export const nonFormatKeys = [
  'has_bulk_rna_seq'
]

// All combinations of MODALITY_PROJECT or MODALITY_SAMPLE supported.
// Used to display additonal information on download modals.
// TODO: Break this into two separate objects
export const modalityResourceInfo = {
  SINGLE_CELL_PROJECT: {
    texts: {},
    learn_more: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.what_downloading_project
    }
  },
  SINGLE_CELL_SAMPLE: {
    texts: {},
    learn_more: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.what_downloading_sample
    }
  },
  SPATIAL_PROJECT: {
    texts: {},
    learn_more: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.what_downloading_spatial
    }
  },
  SPATIAL_SAMPLE: {
    texts: {},
    learn_more: {
      label: 'here',
      text: 'Learn more about what you can expect in your download file',
      url: config.links.what_downloading_spatial
    }
  },
  MULTIPLEXED_PROJECT: {
    texts: {},
    warning_text: {
      link: {
        label: 'Learn more',
        url: config.links.what_downloading_mulitplexed
      },
      text: 'This project contains multiplexed samples.'
    }
  },
  MULTIPLEXED_SAMPLE: {
    fetchRecommended: true,
    texts: {
      text_only: 'This is a multiplexed sample.',
      multiplexed_with: {
        text: 'It has been multiplexed with the following samples.'
      }
    },
    learn_more: {
      label: 'here',
      text: 'Learn more about multiplexed samples ',
      url: config.links.what_downloading_mulitplexed
    },
    warning_text: {
      text: 'If you are planning to work with more than one multiplexed sample, we recommend downloading the entire project.'
    }
  }
}

// For now, this is always the same.
export const metadata = 'Project and Sample Metadata'
