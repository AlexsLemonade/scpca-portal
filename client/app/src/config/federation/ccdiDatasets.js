// A list of allowed CCDL names for CCDI deep links
// Aligns with api/scpca_portal/enums/ccdl_dataset_names.py
// TODO: Multiplexed and spatial samples are excluded for now (revisit later)
export const allowedCCDLNames = [
  'SINGLE_CELL_SINGLE_CELL_EXPERIMENT',
  'SINGLE_CELL_SINGLE_CELL_EXPERIMENT_MERGED',
  'SINGLE_CELL_ANN_DATA',
  'SINGLE_CELL_ANN_DATA_MERGED'
]
