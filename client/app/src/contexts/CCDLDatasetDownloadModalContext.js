import React, { createContext, useEffect, useRef, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useAnalytics } from 'hooks/useAnalytics'
import { api } from 'api'
import { getDateISO } from 'helpers/getDateISO'
import { filterPartialObject } from 'helpers/filterPartialObject'
import { uniqueArrayByKey } from 'helpers/uniqueArray'
import { getReadable } from 'helpers/getReadable'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { sortOnKeyByOrder } from 'helpers/sortOnKeyByOrder'
import { formatOrder, modalityOrder } from 'config/ccdlDatasets'
import { allowedCCDLNames } from 'config/federation/ccdiDatasets'

export const CCDLDatasetDownloadModalContext = createContext({})

export const CCDLDatasetDownloadModalContextProvider = ({
  project,
  datasets,
  ccdlName,
  children
}) => {
  const { email, token, createToken, surveyListForm } = useScPCAPortal()
  const { trackDataset } = useAnalytics()

  const initializeDeepLink = useRef(null)

  const [showing, setShowing] = useState(false)

  const [selectedDataset, setSelectedDataset] = useState(null)

  // CCDI deep links for valid CCDLNames
  const [deepLinkDataset, setDeepLinkDataset] = useState(null)
  const [isValidDeepLink, setIsValidDeepLink] = useState(false) // Display a warning for invalid deep link selection

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

  const getFormatLabel = (d) =>
    d.ccdl_modality === 'SPATIAL'
      ? getReadable('SPATIAL_SPACERANGER')
      : getReadable(d.format)

  // Set deepLinkDataset matching ccdlName
  useEffect(() => {
    if (!ccdlName || !datasets || datasets.length === 0) return

    // If CCDLName Dataset containing multiplexed samples, exclude them by default
    const selectedCCDLName = isMultiplexedAvailable
      ? 'SINGLE_CELL_SINGLE_CELL_EXPERIMENT_NO_MULTIPLEXED'
      : ccdlName

    const dataset =
      datasets.find(
        (d) =>
          allowedCCDLNames.includes(ccdlName) &&
          d.ccdl_name === selectedCCDLName
      ) ?? datasets[0]

    setIsValidDeepLink(dataset.ccdl_name === selectedCCDLName)
    setDeepLinkDataset(dataset)
  }, [ccdlName, isMultiplexedAvailable])

  // Open the modal on page load for deep link
  useEffect(() => {
    if (!deepLinkDataset) return
    // State changes via deep link initialization
    initializeDeepLink.current = true

    setModality(deepLinkDataset.ccdl_modality)
    setFormat(deepLinkDataset.format)
    setIncludesMerged(deepLinkDataset.includes_files_merged)
    setExcludeMultiplexed(true) // Multiplexed samples are excluded by default

    setSelectedDataset(deepLinkDataset)
    setShowing(true)
  }, [deepLinkDataset])

  // on datasets change either reset values or set modality defaults
  useEffect(() => {
    if (!datasets || datasets.length === 0) {
      setSelectedDataset(null)

      setModality(null)
      setFormat(null)
      setIncludesMerged(null)
      setExcludeMultiplexed(null)

      setIsMergedObjectsAvailable(null)
      setIsMultiplexedAvailable(null)

      setModalityOptions([])
      setFormatOptions([])
    } else {
      const [defaultModality] = modalityOrder
      setModality(defaultModality)

      setModalityOptions(
        sortOnKeyByOrder(
          getReadableOptions(datasets.map((d) => d.ccdl_modality)),
          'value',
          modalityOrder
        )
      )

      setIsMergedObjectsAvailable(
        datasets.some((dataset) => dataset.includes_files_merged)
      )
      setIsMultiplexedAvailable(
        datasets.some((dataset) => dataset.includes_files_multiplexed)
      )
    }
    // reset download state vars on datasets change
    setDownloadDataset(false)
    setDownloadableDataset(null)
  }, [datasets])

  // on modality change, set format and merged available defaults
  useEffect(() => {
    if (modality) {
      if (!initializeDeepLink.current) {
        const [defaultFormat] = formatOrder
        setFormat(defaultFormat)
      }

      setFormatOptions(
        sortOnKeyByOrder(
          uniqueArrayByKey(
            datasets
              .filter((d) => d.ccdl_modality === modality)
              .map((d) => ({
                label: getFormatLabel(d), // We override this to present the spatial format
                value: d.format
              })),
            'value'
          ),
          'value',
          formatOrder
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
    if (initializeDeepLink.current) {
      initializeDeepLink.current = false
      return
    }

    if (isMultiplexedAvailable)
      if (format === 'SINGLE_CELL_EXPERIMENT') {
        setExcludeMultiplexed(false)
      } else if (format === 'ANN_DATA') {
        setExcludeMultiplexed(true)
      }
  }, [format, isMultiplexedAvailable])

  // on selected options change, select dataset
  useEffect(() => {
    // handle case where modal is closed and reopened without refresh
    if (!showing) return

    if (datasets.length === 1) {
      setSelectedDataset(datasets[0])
      setDownloadDataset(true)
      return
    }

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
  }, [modality, format, includesMerged, excludeMultiplexed, showing])

  // download file
  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.ccdlDatasets.get(
        selectedDataset.id,
        token
      )
      if (downloadRequest.isOk) {
        trackDataset(selectedDataset)
        surveyListForm.submit({ email, scpca_last_download_date: getDateISO() })
        window.open(downloadRequest.response.download_url)
        setDownloadableDataset(downloadRequest.response)
      } else if (downloadRequest.status === 403) {
        await createToken()
      } else {
        // NOTE: there isn't much we can do here to recover.
        console.error(
          'An error occurred while trying to get the download url for:',
          selectedDataset.id
        )
      }
    }

    if (
      downloadDataset &&
      !downloadableDataset &&
      selectedDataset &&
      token &&
      showing
    )
      asyncFetch()
  }, [downloadDataset, downloadableDataset, selectedDataset, token, showing])

  // reset to selection on close
  useEffect(() => {
    // TODO: look into persisting downloadableDataset for portal wide between modal close-opens
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
        isValidDeepLink,
        modalityOptions,
        formatOptions,
        downloadDataset,
        setDownloadDataset,
        downloadableDataset,
        project,
        deepLinkDataset,
        datasets,
        token
      }}
    >
      {children}
    </CCDLDatasetDownloadModalContext.Provider>
  )
}
