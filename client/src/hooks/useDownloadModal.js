import { useEffect, useState } from 'react'
import { useAnalytics } from 'hooks/useAnalytics'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { getDateISO } from 'helpers/getDateISO'
import { getDefaultComputedFile } from 'helpers/getDefaultComputedFile'
import { hasMultiple } from 'helpers/hasMultiple'

export const useDownloadModal = (
  initialResource,
  initialPublicComputedFile,
  isActive
) => {
  const { token, email, surveyListForm, createToken } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const [resource, setResource] = useState(initialResource)
  const [publicComputedFile, setPublicComputedFile] = useState(
    initialPublicComputedFile
  )
  const [download, setDownload] = useState(false)
  const hasMultipleFiles = hasMultiple(resource.computed_files)
  // states that dictate what the modal can show
  const isDownloadReady = download && token
  const isOptionsReady = !publicComputedFile && hasMultipleFiles
  const isSampleMetadataOnly = publicComputedFile?.metadata_only
  const isTokenReady = !token && publicComputedFile
  // text information
  const verb = isDownloadReady ? 'Downloading' : 'Download'
  const resourceType = resource.samples ? 'Project' : 'Sample'
  const modalTitle = isSampleMetadataOnly
    ? `${verb} Sample Metadata`
    : `${verb} ${resourceType}`
  const defaultComputedFile = getDefaultComputedFile(resource)
  const hasDownloadOptions =
    publicComputedFile && hasMultipleFiles && !initialPublicComputedFile

  const tryDownload = () => {
    if (download && download.download_url) {
      const { type, project, sample } = publicComputedFile
      trackDownload(type, project, sample)
      surveyListForm.submit({ email, scpca_last_download_date: getDateISO() })
      window.open(download.download_url)
    }
  }

  const handleSelectFile = (file, newResource) => {
    setDownload(false)
    if (newResource) setResource(newResource)
    setPublicComputedFile(file)
  }

  // Configure State
  useEffect(() => {
    if (initialResource && !resource) setResource(initialResource)

    if (initialPublicComputedFile && !publicComputedFile)
      setPublicComputedFile(initialPublicComputedFile)

    if (!initialPublicComputedFile)
      setPublicComputedFile(hasMultipleFiles ? null : defaultComputedFile)
  }, [resource])

  // Download when ready
  useEffect(() => {
    if (!isActive) {
      setDownload(false)
    }

    const asyncFetch = async () => {
      const downloadRequest = await api.computedFiles.get(
        publicComputedFile.id,
        token
      )
      if (downloadRequest.isOk) {
        // try to open download
        const { type, project, sample } = publicComputedFile
        trackDownload(type, project, sample)
        surveyListForm.submit({
          email,
          scpca_last_download_date: getDateISO()
        })
        window.open(downloadRequest.response.download_url)
        setDownload(downloadRequest.response)
        // Clear out the selected file if it was not explicitly set.
        // This allows to select a different configuration.
        if (!initialPublicComputedFile) setPublicComputedFile(null)
      } else if (downloadRequest.status === 403) {
        await createToken()
      } else {
        // NOTE: there isnt much we can do here to recover.
        console.error(
          'An error occurred while trying to get the download url for:',
          publicComputedFile.id
        )
      }
    }

    if (!download && token && isActive && publicComputedFile) asyncFetch()
  }, [download, token, isActive, publicComputedFile])

  return {
    resource,
    handleSelectFile,
    modalTitle,
    tryDownload,
    publicComputedFile,
    setPublicComputedFile,
    download,
    setDownload,
    hasDownloadOptions,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  }
}

export default useDownloadModal
