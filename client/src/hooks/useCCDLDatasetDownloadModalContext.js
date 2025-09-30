import { useContext, useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { CCDLDatasetDownloadModalContext } from 'contexts/CCDLDatasetDownloadModalContext'
import { formatNames } from 'config/ccdlDatasets'

export const useCCDLDatasetDownloadModalContext = () => {
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
    isMergedObjectsAvailable,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions,
    project,
    datasets
  } = useContext(CCDLDatasetDownloadModalContext)

  const [showing, setShowing] = useState(false)

  const { token, createToken } = useScPCAPortal()
  const [downloadDataset, setDownloadDataset] = useState(
    datasets.length === 1 ? datasets[0] : null
  )
  const [downloadLink, setDownloadLink] = useState(null)

  const isTokenReady = !token
  const isOptionsReady = datasets?.length > 1 && !!token && !downloadDataset
  const isDownloadReady = !!downloadDataset && !!token

  const modalModalityNames = {
    SINGLE_CELL: 'Data',
    SPATIAL: 'Spatial Data'
  }

  const getModalTitle = (dataset) => {
    const modalTitleAction = isDownloadReady ? 'Downloading' : 'Download'
    const modalityName =
      dataset.format === 'METADATA'
        ? 'Sample Metadata'
        : modalModalityNames[dataset.ccdl_modality]
    const modalTitleResource = dataset.ccdl_project_id
      ? 'Project'
      : `Portal-wide ${modalityName}`
    const asFormat =
      dataset.ccdl_modality === 'SINGLE_CELL'
        ? `as ${formatNames[dataset.format]}`
        : ''
    return `${modalTitleAction} ${modalTitleResource} ${asFormat}`.trim()
  }
  const modalTitle = getModalTitle(selectedDataset)

  // downloadDataset should be set immediately for ccdl portal wide and project metadata downloads
  useEffect(() => {
    if (selectedDataset && datasets.length === 1) {
      setDownloadDataset(selectedDataset)
    }
  }, [datasets, selectedDataset])

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

  useEffect(() => {
    if (!showing) {
      setDownloadLink(null)
      // downloadDataset needs to be unset each time the modal is closed for ccdl project datasets
      if (datasets.length > 1) setDownloadDataset(null)
    }
  }, [showing])

  return {
    showing,
    setShowing,
    modalTitle,
    isDownloadReady,
    isTokenReady,
    isOptionsReady,
    downloadDataset,
    setDownloadDataset,
    downloadLink,
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
    project,
    datasets
  }
}
