import React, { createContext, useEffect, useState } from 'react'

export const CCDLDatasetDownloadOptionsContext = createContext({})

export const CCDLDatasetDownloadOptionsContextProvider = ({
  project,
  datasets,
  children
}) => {
  const defaultDataset = datasets[0]

  const [selectedDataset, setSelectedDataset] = useState(defaultDataset)
  const [modality, setModality] = useState()
  const [format, setFormat] = useState()
  const [includesMerged, setIncludesMerged] = useState()
  const [excludeMultiplexed, setExcludeMultiplexed] = useState()

  // TODO: add a helper that allows passing in an object and have it match on that object
  useEffect(() => {
    const includesMultiplexed =
      project.has_multiplexed_data &&
      !excludeMultiplexed &&
      modality === 'SINGLE_CELL' &&
      format === 'SINGLE_CELL_EXPERIMENT'

    setSelectedDataset(
      datasets.find(
        (d) =>
          d.ccdl_modality === modality &&
          d.format === format &&
          d.includes_files_merged === includesMerged &&
          d.includes_files_multiplexed === includesMultiplexed
      )
    )
  }, [modality, format, includesMerged, excludeMultiplexed])

  return (
    <CCDLDatasetDownloadOptionsContext.Provider
      value={{
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
      }}
    >
      {children}
    </CCDLDatasetDownloadOptionsContext.Provider>
  )
}
