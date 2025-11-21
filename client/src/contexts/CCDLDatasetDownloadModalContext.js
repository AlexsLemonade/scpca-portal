import React, { createContext, useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { filterPartialObject } from 'helpers/filterPartialObject'
import { uniqueArray } from 'helpers/uniqueArray'

export const CCDLDatasetDownloadModalContext = createContext({})

export const CCDLDatasetDownloadModalContextProvider = ({
  project,
  datasets,
  children
}) => {
  const { token, createToken } = useScPCAPortal()

  const [showing, setShowing] = useState(false)

  const [selectedDataset, setSelectedDataset] = useState(null)

  // set when `datasets` changes
  const [modality, setModality] = useState(null)
  const [format, setFormat] = useState(null)
  const [includesMerged, setIncludesMerged] = useState(null)
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(null)

  const [downloadDataset, setDownloadDataset] = useState(false)
  const [downloadableDataset, setDownloadableDataset] = useState(null)

  const [isMergedObjectsAvailable, setIsMergedObjectsAvailable] = useState(null)
  const [isMultiplexedAvailable, setIsMultiplexedAvailable] = useState(null)

  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  // on datasets change
  useEffect(() => {
    if (!datasets || datasets.length === 0) {
      setSelectedDataset(null)

      setModality(null)
      setFormat(null)
      setIncludesMerged(null)
      setExcludeMultiplexed(null)

      setDownloadDataset(false)
      setDownloadableDataset(null)

      setIsMergedObjectsAvailable(null)
      setIsMultiplexedAvailable(null)

      setModalityOptions([])
      setFormatOptions([])
    } else {
      const defaultDataset =
        datasets.length > 1
          ? datasets.find(
              (d) => d.ccdl_name === 'SINGLE_CELL_SINGLE_CELL_EXPERIMENT'
            )
          : datasets[0]
      setSelectedDataset(defaultDataset)

      setModality(defaultDataset.ccdl_modality)
      setFormat(defaultDataset.format)
      setIncludesMerged(defaultDataset.includes_files_merged)
      setExcludeMultiplexed(defaultDataset.includes_files_multiplexed)

      setDownloadDataset(datasets.length === 1)

      setIsMergedObjectsAvailable(
        datasets.some((dataset) => dataset.includes_files_merged)
      )
      setIsMultiplexedAvailable(
        datasets.some((dataset) => dataset.includes_files_multiplexed)
      )

      setModalityOptions(uniqueArray(datasets.map((d) => d.ccdl_modality)))
    }
  }, [datasets])

  // on selectedDataset change (displayed formatOptions are dependent on selectedDataset)
  useEffect(() => {
    if (selectedDataset) {
      setFormatOptions(
        uniqueArray(
          datasets
            .filter((d) => d.ccdl_modality === selectedDataset.ccdl_modality)
            .map((d) => d.format)
        )
      )
    } else {
      setFormatOptions([])
    }
  }, [selectedDataset])

  // on selected options change
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
    } else {
      console.error(
        `There was an error selecting the correct dataset. ${matches.length} datasets were matched on the previous query.`
      )
    }
  }, [modality, format, includesMerged, excludeMultiplexed])

  // download file
  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.ccdlDatasets.get(
        selectedDataset.id,
        token
      )
      if (downloadRequest.isOk) {
        window.open(downloadRequest.response.download_url)
        setDownloadableDataset(downloadRequest.response)
      } else if (downloadRequest.status === 403) {
        await createToken()
      } else {
        // NOTE: there isnt much we can do here to recover.
        console.error(
          'An error occurred while trying to get the download url for:',
          selectedDataset.id
        )
      }
    }

    if (downloadDataset && !downloadableDataset && token && showing)
      asyncFetch()
  }, [downloadDataset, downloadableDataset, token, showing])

  // reset to selection on close
  useEffect(() => {
    if (!showing) {
      setDownloadDataset(false)
      setDownloadableDataset(null)
    }
  }, [showing])

  return (
    <CCDLDatasetDownloadModalContext.Provider
      value={{
        showing,
        setShowing,
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
        downloadDataset,
        setDownloadDataset,
        downloadableDataset,
        project,
        datasets,
        token
      }}
    >
      {children}
    </CCDLDatasetDownloadModalContext.Provider>
  )
}
