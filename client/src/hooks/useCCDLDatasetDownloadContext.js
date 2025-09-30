import { useContext } from 'react'
import { CCDLDatasetDownloadContext } from 'contexts/CCDLDatasetDownloadContext'

export const useCCDLDatasetDownloadContext = () => {
  const {
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed,
    selectedDataset,
    isMergedObjectsAvailable,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions,
    project,
    datasets
  } = useContext(CCDLDatasetDownloadContext)

  return {
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed,
    selectedDataset,
    isMergedObjectsAvailable,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions,
    project,
    datasets
  }
}
