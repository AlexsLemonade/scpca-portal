// takes a dataset and returns an array of readable file items
import { modalityNames, formatNames } from 'config/ccdlDatasets'

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
      ? `${modalityNames[modality]}, CITE-seq data`
      : modalityNames[modality]
    items.push(`${modalityItem} as ${formatNames[format]}`)
  }

  if (modality === 'SPATIAL') {
    items.push(modalityNames[modality])
  }

  if (hasMultiplexed && !isMetadataDataset) {
    items.push(`Multiplexed single-cell data as ${formatNames[format]}`)
  }

  if (hasBulk && !isMetadataDataset) {
    items.push('Bulk RNA-Seq data')
  }

  if (seperateCiteSeqFile) {
    items.push(`CITE-seq data as ${formatNames[format]}`)
  }

  const metadataItem = portalWideMetadataOnly
    ? 'Sample metadata from all projects'
    : 'Project and Sample Metadata'

  items.push(metadataItem)

  return items
}

export default getCCDLDatasetFileItems
