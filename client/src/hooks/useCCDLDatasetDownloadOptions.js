import { useEffect, useState } from 'react'

export const useCCDLDatasetDownloadOptions = (datasets) => {
  const getModalityOptions = (ds) => {
    return [...new Set(ds.map((d) => d.ccdl_modality))]
  }
  const getFormatOptions = (ds, modality = 'SINGLE_CELL') => {
    if (modality === 'SPATIAL') return ['SINGLE_CELL_EXPERIMENT']

    return [...new Set(ds.map((d) => d.format))]
  }
  const [modalityOptions, setModalityOptions] = useState(
    getModalityOptions(datasets)
  )
  const [formatOptions, setFormatOptions] = useState(getFormatOptions(datasets))

  const [modality, setModality] = useState(datasets[0].ccdl_modality)
  const [format, setFormat] = useState(datasets[0].format)
  const [includesMerged, setIncludesMerged] = useState(false)
  const [isMergedObjectsAvailable, setIsMergedObjectsAvailable] = useState(
    datasets.some((dataset) => dataset.includes_files_merged)
  )
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [isExcludeMultiplexedAvailable, setIsExcludeMultiplexedAvailable] =
    useState(datasets.some((dataset) => dataset.includes_files_multiplexed))

  const [showingDataset, setShowingDataset] = useState(datasets[0])

  useEffect(() => {
    setModalityOptions(getModalityOptions(datasets))
    setIsMergedObjectsAvailable(
      datasets.some((dataset) => dataset.includes_files_merged)
    )
    setIsExcludeMultiplexedAvailable(
      datasets.some((dataset) => dataset.includes_files_multiplexed)
    )
  }, [datasets])

  useEffect(() => {
    setFormatOptions(getFormatOptions(datasets, modality))
  }, [datasets, modality])

  useEffect(() => {
    setShowingDataset(
      datasets.find(
        (d) =>
          d.ccdl_modality === modality &&
          d.format === format &&
          d.includes_files_merged === includesMerged &&
          d.includes_files_multiplexed ===
            (isExcludeMultiplexedAvailable && !excludeMultiplexed)
      )
    )
  }, [modality, format, includesMerged, excludeMultiplexed])

  return {
    modalityOptions,
    formatOptions,
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    isMergedObjectsAvailable,
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable,
    showingDataset
  }
}

export default useCCDLDatasetDownloadOptions
