import { getReadable } from 'helpers/getReadable'
import { readableCCDLFileItems, readableFiles } from 'config/readableNames'

const readableFileDict = { ...readableCCDLFileItems, ...readableFiles }

const keys = {
  SINGLE_CELL: 'SINGLE_CELL_DATA',
  SPATIAL: 'SPATIAL_DATA',
  MULTIPLEXED_DATA: 'MULTIPLEXED_DATA',
  BULK_DATA: 'BULK_DATA',
  CITE_SEQ_DATA: 'CITE_SEQ_DATA',
  PORTAL_WIDE_METADATA: 'PORTAL_WIDE_METADATA',
  PROJECT_METADATA: 'PROJECT_METADATA'
}

const getReadableFile = (key) => {
  const fileItem = readableFileDict[key]
  if (!fileItem) {
    console.error(`Key ${key} is not present in readable file items for CCDL`)
  }
  return fileItem
}

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

  const isMetadataDataset = format === 'METADATA'
  const portalWideMetadataOnly = isMetadataDataset && !projectId
  const combinedCiteSeqFile = hasCiteSeq && format === 'SINGLE_CELL_EXPERIMENT'
  const separateCiteSeqFile = hasCiteSeq && format === 'ANN_DATA'

  const metadataKey = portalWideMetadataOnly
    ? keys.PORTAL_WIDE_METADATA
    : keys.PROJECT_METADATA

  const readableModality = keys[modality] ? getReadableFile(keys[modality]) : ''
  const readableFormat = getReadable(format)

  // Modality file items
  if (modality === 'SINGLE_CELL') {
    const modalityItem = combinedCiteSeqFile
      ? `${readableModality}, ${getReadableFile(keys.CITE_SEQ_DATA)}`
      : readableModality
    items.push(`${modalityItem} as ${readableFormat}`)
  }
  if (modality === 'SPATIAL') {
    // exception to the rule: spaceranger as files is always one word lower
    items.push(`${readableModality} as spaceranger`)
  }

  // Other modality/data file items
  if (!isMetadataDataset) {
    if (hasMultiplexed) {
      items.push(
        `${getReadableFile(keys.MULTIPLEXED_DATA)} as ${readableFormat}`
      )
    }
    if (hasBulk) {
      items.push(getReadableFile(keys.BULK_DATA))
    }
  }

  // Cite-seq for AnnData
  if (separateCiteSeqFile) {
    items.push(`${getReadableFile(keys.CITE_SEQ_DATA)} as ${readableFormat}`)
  }

  // Metadata file items
  items.push(getReadableFile(metadataKey))

  return items
}

export default getCCDLDatasetFileItems
