import React, { createContext, useEffect, useState } from 'react'
import { filterPartialObject } from 'helpers/filterPartialObject'
import { uniqueArray } from 'helpers/uniqueArray'

export const CCDLDatasetDownloadContext = createContext({})

export const CCDLDatasetDownloadContextProvider = ({
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

  useEffect(() => {
    const query = {
      ccdl_modality: modality,
      format,
      includes_files_merged: includesMerged
    }
    if (project && project.has_multiplexed_data) {
      query.includes_files_multiplexed = !excludeMultiplexed
    }

    const matches = filterPartialObject(datasets, query)
    if (matches.length === 1) {
      setSelectedDataset(matches[0])
    }
  }, [modality, format, includesMerged, excludeMultiplexed])

  return (
    <CCDLDatasetDownloadContext.Provider
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
        isMergedObjectsAvailable,
        isMultiplexedAvailable,
        modalityOptions,
        formatOptions,
        project
      }}
    >
      {children}
    </CCDLDatasetDownloadContext.Provider>
  )
}
