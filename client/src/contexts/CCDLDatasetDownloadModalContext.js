import React, { createContext, useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { filterPartialObject } from 'helpers/filterPartialObject'
import { uniqueArrayByKey } from 'helpers/uniqueArray'
import { getReadable } from 'helpers/getReadable'
import { getReadableOptions } from 'helpers/getReadableOptions'

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

  const [modalityOptions, setModalityOptions] = useState(null)
  const [formatOptions, setFormatOptions] = useState(null)

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

      setModalityOptions(null)
      setFormatOptions(null)
    } else {
      const defaultDataset = datasets[0]
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

      setModalityOptions(
        getReadableOptions(datasets.map((d) => d.ccdl_modality))
      )
    }
  }, [datasets])

  // on selectedDataset change (displayed formatOptions are dependent on selectedDataset)
  useEffect(() => {
    if (selectedDataset) {
      setFormatOptions(
        uniqueArrayByKey(
          datasets
            .filter((d) => d.ccdl_modality === selectedDataset.ccdl_modality)
            .map((d) => ({
              label:
                // We override this to present the spatial format
                d.ccdl_modality === 'SPATIAL'
                  ? getReadable('SPATIAL_SPACERANGER')
                  : getReadable(d.format),
              value: d.format
            })),
          'value'
        )
      )
    } else {
      setFormatOptions(null)
    }
  }, [selectedDataset])

  // reset format to default upon modality change
  useEffect(() => {
    setFormat('SINGLE_CELL_EXPERIMENT')
  }, [modality])

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
