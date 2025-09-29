import { useContext } from 'react'
import { CCDLDatasetDownloadOptionsContext } from 'contexts/CCDLDatasetDownloadOptionsContext'
import { uniqueArray } from 'helpers/uniqueArray'

export const useCCDLDatasetDownloadOptions = () => {
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
    project,
    datasets
  } = useContext(CCDLDatasetDownloadOptionsContext)

  const isMergedObjectsAvailable = datasets.some(
    (dataset) => dataset.includes_files_merged
  )
  const isMultiplexedAvailable = datasets.some(
    (dataset) => dataset.includes_files_multiplexed
  )

  const modalityOptions = uniqueArray(datasets.map((d) => d.ccdl_modality))

  const formatOptions = uniqueArray(
    datasets
      .filter((d) => d.ccdl_modality === selectedDataset.ccdl_modality)
      .map((d) => d.format)
  )

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
    project
  }
}
