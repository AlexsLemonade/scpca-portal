import { getReadable, getReadableCCDLFileItems } from 'helpers/getReadable'

// takes a dataset and returns an array of readable file items
export const getCCDLDatasetFileItems = (dataset) => {
  const items = []

  const {
    ccdl_project_id: projectId,
    format,
    ccdl_modality: modality,
    includes_files_bulk: hasBulk,
    includes_files_cite_seq: hasCiteSeq,
    includes_files_multiplexed: hasMultiplexed
  } = dataset

  const isMetadataDataset = format === 'METADATA'
  const portalWideMetadataOnly = isMetadataDataset && !projectId
  const combinedCiteSeqFile = hasCiteSeq && format === 'SINGLE_CELL_EXPERIMENT'
  const seperateCiteSeqFile = hasCiteSeq && format === 'ANN_DATA'

  if (modality === 'SINGLE_CELL') {
    const modalityItem = combinedCiteSeqFile
      ? `${getReadableCCDLFileItems(
          'SINGLE_CELL_DATA'
        )}, ${getReadableCCDLFileItems('CITE_SEQ_DATA')}`
      : getReadableCCDLFileItems('SINGLE_CELL_DATA')
    items.push(`${modalityItem} as ${getReadable(format)}`)
  }

  if (modality === 'SPATIAL') {
    // exception to the rule: spaceranger as files is always one word lower
    items.push(`${getReadableCCDLFileItems('SPATIAL_DATA')} as spaceranger`)
  }

  if (hasMultiplexed && !isMetadataDataset) {
    items.push(
      `${getReadableCCDLFileItems('MULTIPLEXED_DATA')} as ${getReadable(
        format
      )}`
    )
  }

  if (hasBulk && !isMetadataDataset) {
    items.push(getReadableCCDLFileItems('BULK_DATA'))
  }

  if (seperateCiteSeqFile) {
    items.push(
      `${getReadableCCDLFileItems('CITE_SEQ_DATA')} as ${getReadable(format)}`
    )
  }

  const metadataItem = portalWideMetadataOnly
    ? getReadableCCDLFileItems('PORTAL_WIDE_METADATA')
    : getReadableCCDLFileItems('PROJECT_METADATA')

  items.push(metadataItem)

  return items
}

export default getCCDLDatasetFileItems
