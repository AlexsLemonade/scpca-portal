import { getReadable } from 'helpers/getReadable'
import { fileKeys, fileValues } from 'config/translations'

// takes a dataset and returns an array of readable file items
export const getCCDLDatasetFileItems = (dataset) => {
  const {
    ccdl_project_id: projectId,
    format,
    ccdl_modality: modality,
    includes_files_bulk: hasBulk,
    includes_files_cite_seq: hasCiteSeq,
    includes_files_multiplexed: hasMultiplexed
  } = dataset

  const items = []

  const readableModality = modality ? getReadable(modality, fileValues) : ''
  const readableFormat = getReadable(format)

  const isMetadataDataset = format === 'METADATA'
  const isPortalWideMetadata = isMetadataDataset && !projectId
  const metadataItem = isPortalWideMetadata
    ? 'Sample metadata from all projects'
    : 'Project and Sample Metadata'

  const isCombinedCiteSeqFile =
    modality === 'SINGLE_CELL' &&
    hasCiteSeq &&
    format === 'SINGLE_CELL_EXPERIMENT'
  const singleCellModalityItem = isCombinedCiteSeqFile
    ? `${readableModality}, ${fileKeys.includes_files_cite_seq}`
    : readableModality

  const isSeparateCiteSeqFile = hasCiteSeq && format === 'ANN_DATA'

  if (isMetadataDataset) {
    return [metadataItem]
  }

  // Modality file items
  if (modality === 'SINGLE_CELL') {
    items.push(`${singleCellModalityItem} as ${readableFormat}`)
  }

  if (modality === 'SPATIAL') {
    // exception to the rule: spaceranger as files is always one word lower
    items.push(`${readableModality} as spaceranger`)
  }

  // Cite-seq for AnnData
  if (isSeparateCiteSeqFile) {
    items.push(`${fileKeys.includes_files_cite_seq} as ${readableFormat}`)
  }

  // Other modality/data file items
  if (hasMultiplexed) {
    items.push(`${fileKeys.includes_files_multiplexed} as ${readableFormat}`)
  }

  if (hasBulk) {
    items.push(fileKeys.includes_files_bulk)
  }

  // Metadata file items
  items.push(metadataItem)

  return items
}

export default getCCDLDatasetFileItems
