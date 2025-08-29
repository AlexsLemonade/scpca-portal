import { useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'

export const useCCDLDatasetDownloadModal = (initialDatasets, isActive) => {
  const { token, createToken } = useScPCAPortal()
  const [datasets, setDatasets] = useState(initialDatasets)
  const [selectedDataset, setSelectedDataset] = useState(null)
  const [downloadDataset, setDownloadDataset] = useState(null)

  const isTokenReady = !token
  const isOptionsReady = !datasets && token
  const isDownloadReady = downloadDataset && token

  const modalTitle = isDownloadReady
    ? 'Downloading Dataset'
    : 'Download Dataset'

  useEffect(() => {
    setSelectedDataset(null)
    setDownloadDataset(null)

    if (datasets.length === 1) {
      setSelectedDataset()
    }
  }, [datasets])

  useEffect(() => {
    if (!isActive) {
      setSelectedDataset(null)
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
