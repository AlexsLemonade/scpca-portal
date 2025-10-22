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

  const defaultDataset = datasets[0]

  const [showing, setShowing] = useState(false)

  const [selectedDataset, setSelectedDataset] = useState(defaultDataset)
  const [modality, setModality] = useState(defaultDataset.ccdl_modality)
  const [format, setFormat] = useState(defaultDataset.format)
  const [includesMerged, setIncludesMerged] = useState(false)
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)

  const [downloadDataset, setDownloadDataset] = useState(
    datasets.length === 1 ? datasets[0] : null
  )
  const [downloadLink, setDownloadLink] = useState(null)

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
    } else {
      console.error(
        `There was an error selecting the correct dataset. ${matches.length} datasets were matched on the previous query.`
      )
    }
  }, [modality, format, includesMerged, excludeMultiplexed])

  // downloadDataset should be set immediately for ccdl portal wide and project metadata downloads
  useEffect(() => {
    if (selectedDataset && datasets.length === 1) {
      setDownloadDataset(selectedDataset)
    }
  }, [datasets, selectedDataset])

  // download file
  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.ccdlDatasets.get(
        downloadDataset.id,
        token
      )
      if (downloadRequest.isOk) {
        window.open(downloadRequest.response.download_url)
        setDownloadLink(downloadRequest.response.download_url)
      } else if (downloadRequest.status === 403) {
        await createToken()
      } else {
        // NOTE: there isnt much we can do here to recover.
        console.error(
          'An error occurred while trying to get the download url for:',
          downloadDataset.id
        )
      }
    }

    if (downloadDataset && !downloadLink && token && showing) asyncFetch()
  }, [downloadDataset, downloadLink, token, showing])

  // reset to selection on close
  useEffect(() => {
    if (!showing) {
      setDownloadLink(null)
      // downloadDataset needs to be unset each time the modal is closed for ccdl project datasets
      if (datasets.length > 1) setDownloadDataset(null)
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
        downloadLink,
        project,
        datasets,
        token
      }}
    >
      {children}
    </CCDLDatasetDownloadModalContext.Provider>
  )
}
