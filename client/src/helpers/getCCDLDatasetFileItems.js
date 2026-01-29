import { getReadable, getReadableFileItems } from 'helpers/getReadable'

// takes a dataset and returns an array of readable file items
export const getCCDLDatasetFileItems = (dataset) => {
  const items = []

  const {
    ccdl_project_id: projectId,
    format,
    ccdl_modality: modality,
    includes_files_bulk: hasBulk,
    includes_files_cite_seq: hasCiteSeq,
    includes_files_multiplexed: hasMultiplexed,
    includes_files_merged: hasMerged
  } = dataset

  const isMetadataDataset = format === 'METADATA'
  const portalWideMetadataOnly = isMetadataDataset && !projectId
  const combinedCiteSeqFile = hasCiteSeq && format === 'SINGLE_CELL_EXPERIMENT'
  const seperateCiteSeqFile = hasCiteSeq && format === 'ANN_DATA'

  if (modality === 'SINGLE_CELL') {
    const modalityItem = combinedCiteSeqFile
      ? `${getReadableFileItems('SINGLE_CELL_DATA')}, ${getReadableFileItems(
          'CITE_SEQ_DATA'
        )}`
      : getReadableFileItems('SINGLE_CELL_DATA')
    items.push(`${modalityItem} as ${getReadable(format)}`)
  }

  if (modality === 'SPATIAL') {
    // exception to the rule: spaceranger as files is always one word lower
    items.push(`${getReadableFileItems('SPATIAL_DATA')} as spaceranger`)
  }

  if (hasMultiplexed && !isMetadataDataset & !hasMerged) {
    items.push(
      `${getReadableFileItems('MULTIPLEXED_DATA')} as ${getReadable(format)}`
    )
  }

  if (hasBulk && !isMetadataDataset) {
    items.push(getReadableFileItems('BULK_DATA'))
  }

  if (seperateCiteSeqFile) {
    items.push(
      `${getReadableFileItems('CITE_SEQ_DATA')} as ${getReadable(format)}`
    )
  }

  const metadataItem = portalWideMetadataOnly
    ? getReadableFileItems('PORTAL_WIDE_METADATA')
    : getReadableFileItems('PROJECT_METADATA')

  items.push(metadataItem)

  return items
}

export default getCCDLDatasetFileItems
