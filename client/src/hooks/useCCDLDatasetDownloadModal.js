import { useEffect, useState } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { portalWideDatasets } from 'config/ccdlDatasets'
import { useCCDLDatasetDownloadContext } from 'hooks/useCCDLDatasetDownloadContext'

export const useCCDLDatasetDownloadModal = () => {
  const [showing, setShowing] = useState(false)

  const { token, createToken } = useScPCAPortal()
  const { datasets, selectedDataset } = useCCDLDatasetDownloadContext()
  const [downloadDataset, setDownloadDataset] = useState(
    datasets.length === 1 ? datasets[0] : null
  )
  const [downloadLink, setDownloadLink] = useState(null)

  const isTokenReady = !token
  const isOptionsReady = datasets?.length > 1 && !!token && !downloadDataset
  const isDownloadReady = !!downloadDataset && !!token

  const modalTitleAction = isDownloadReady ? 'Downloading' : 'Download'
  const modalTitleDataset =
    portalWideDatasets[selectedDataset?.ccdl_name]?.modalTitle
  const modalTitleResource = selectedDataset.ccdl_project_id
    ? 'Project'
    : modalTitleDataset
  const modalTitle = `${modalTitleAction} ${modalTitleResource}`

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
    downloadLink
  }
}
