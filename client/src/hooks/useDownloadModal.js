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
  // pass an empty array when no resource
  const hasMultipleFiles = hasMultiple(resource?.computed_file || [])
  // states that dictate what the modal can show
  const isDownloadReady = download && token
  const isOptionsReady = !publicComputedFile && hasMultipleFiles
  const isTokenReady = !token && publicComputedFile
  const isSampleMetadataOnly = publicComputedFile?.metadata_only
  const isPortalMetadataOnly = publicComputedFile?.portal_metadata_only
  // text information
  const verb = isDownloadReady ? 'Downloading' : 'Download'
  // helper for resourceType
  const getResourceType = () => {
    if (!resource) return 'All' // for the portal metadata
    return resource.samples ? 'Project' : 'Sample'
  }
  const resourceType = getResourceType()
  const defaultTitle = `${verb} ${resourceType}`
  const sampleMetadataTitle = `${verb} ${
    isPortalMetadataOnly ? 'All' : ''
  } Sample Metadata`
  const modalTitle = isSampleMetadataOnly ? sampleMetadataTitle : defaultTitle
  const defaultComputedFile = resource
    ? getDefaultComputedFile(resource)
    : undefined
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
