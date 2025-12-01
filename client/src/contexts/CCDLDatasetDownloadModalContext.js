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
  const [includesMerged, setIncludesMerged] = useState(false)
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)

  const [downloadDataset, setDownloadDataset] = useState(false)
  const [downloadableDataset, setDownloadableDataset] = useState(null)

  const [isMergedObjectsAvailable, setIsMergedObjectsAvailable] = useState(null)
  const [isMultiplexedAvailable, setIsMultiplexedAvailable] = useState(null)

  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  const modalityOrder = ['SINGLE_CELL', 'SPATIAL']
  const formatOrder = ['SINGLE_CELL_EXPERIMENT', 'ANN_DATA']

  const sortByModalityOrder = (items) => {
    items.sort((a, b) => {
      return modalityOrder.indexOf(a.value) - modalityOrder.indexOf(b.value)
    })

    return items
  }
  const sortByFormatOrder = (items) => {
    items.sort((a, b) => {
      return formatOrder.indexOf(a.value) - formatOrder.indexOf(b.value)
    })

    return items
  }

  // on datasets change either reset values or set modality defaults
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
      const [defaultModality] = modalityOrder
      setModality(defaultModality)
      setModalityOptions(
        sortByModalityOrder(
          getReadableOptions(datasets.map((d) => d.ccdl_modality))
        )
      )

      setIsMergedObjectsAvailable(
        datasets.some((dataset) => dataset.includes_files_merged)
      )
      setIsMultiplexedAvailable(
        datasets.some((dataset) => dataset.includes_files_multiplexed)
      )

      setDownloadDataset(datasets.length === 1)
    }
  }, [datasets])

  // on modality change, set format and merged available defaults
  useEffect(() => {
    if (modality) {
      const [defaultFormat] = formatOrder
      setFormat(defaultFormat)
      setFormatOptions(
        sortByFormatOrder(
          uniqueArrayByKey(
            datasets
              .filter((d) => d.ccdl_modality === modality)
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
      )
    }
  }, [modality])

  // on modality change, make sure includes value is valid
  useEffect(() => {
    if (modality !== 'SINGLE_CELL') setIncludesMerged(false)
  }, [modality])

  // on format change, set exclude multiplexed defaults
  useEffect(() => {
    if (isMultiplexedAvailable)
      if (format === 'SINGLE_CELL_EXPERIMENT') {
        setExcludeMultiplexed(false)
      } else if (format === 'ANN_DATA') {
        setExcludeMultiplexed(true)
      }
  }, [format, isMultiplexedAvailable])

  // on selected options change, select dataset
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
