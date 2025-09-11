import { useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { portalWideDatasets } from 'config/ccdlDatasetDownloadModal'

export const useCCDLDatasetDownloadModal = (initialDatasets, isActive) => {
  const [showing, setShowing] = useState(false)

  const { token, createToken } = useScPCAPortal()
  const [datasets, setDatasets] = useState(initialDatasets || [])
  const [selectedDataset, setSelectedDataset] = useState(null)
  const [downloadDataset, setDownloadDataset] = useState(null)

  const isTokenReady = !token
  const isOptionsReady = datasets?.length > 1 && !!token
  const isDownloadReady = !!downloadDataset && !!token

  const modalTitleAction = isDownloadReady ? 'Downloading' : 'Download'
  const modalTitleDataset =
    portalWideDatasets[selectedDataset?.ccdl_name]?.modalTitleDataset
  const modalTitleResource = datasets[0].ccdl_project_id
    ? 'Project'
    : modalTitleDataset
  const modalTitle = `${modalTitleAction} ${modalTitleResource}`

  useEffect(() => {
    setDatasets(initialDatasets || [])
    setSelectedDataset(null)
    setDownloadDataset(null)
  }, [initialDatasets])

  useEffect(() => {
    setDownloadDataset(null)

    if (datasets?.length === 1) {
      setSelectedDataset(datasets[0])
    } else {
      setSelectedDataset(null)
    }
  }, [datasets])

  useEffect(() => {
    if (!isActive) {
      setDownloadDataset(null)
    }

    const asyncFetch = async () => {
      const downloadRequest = await api.ccdlDatasets.get(
        selectedDataset.id,
        token
      )
      if (downloadRequest.isOk) {
        window.open(downloadRequest.response.download_url)
        setDownloadDataset(downloadRequest.response)
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
    if (selectedDataset && !downloadDataset && token && isActive) asyncFetch()
  }, [selectedDataset, downloadDataset, token, isActive])

  const tryDownload = () => {
    if (downloadDataset && downloadDataset.download_url) {
      window.open(downloadDataset.download_url)
    }
  }

  return {
    showing,
    setShowing,
    token,
    modalTitle,
    tryDownload,
    datasets,
    setDatasets,
    setSelectedDataset,
    downloadDataset,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  }
}
