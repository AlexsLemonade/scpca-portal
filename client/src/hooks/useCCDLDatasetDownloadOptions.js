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
  const [hasMerged, setHasMerged] = useState(datasets[0].includes_files_merged)
  const [hasMultiplexed, setHasMultiplexed] = useState(
    datasets[0].includes_files_multiplexed
  )

  const [showingDataset, setShowingDataset] = useState(datasets[0])

  useEffect(() => {
    setModalityOptions(getModalityOptions(datasets))
    setFormatOptions(getFormatOptions(datasets, modality))
  }, [datasets, modality])

  useEffect(() => {
    setShowingDataset(
      datasets.find(
        (d) =>
          d.ccdl_modality === modality &&
          d.format === format &&
          d.includes_files_merged === hasMerged &&
          d.includes_files_multiplexed === hasMultiplexed
      )
    )
  }, [modality, format, hasMerged, hasMultiplexed])

  return {
    modalityOptions,
    formatOptions,
    modality,
    setModality,
    format,
    setFormat,
    hasMerged,
    setHasMerged,
    hasMultiplexed,
    setHasMultiplexed,
    showingDataset
  }
}

export default useCCDLDatasetDownloadOptions
