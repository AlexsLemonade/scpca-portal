/* eslint-disable no-nested-ternary */
import React, { useEffect, useState } from 'react'
import { useAnalytics } from 'hooks/useAnalytics'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadToken } from 'components/DownloadToken'
import { Icon } from 'components/Icon'
import { Modal, ModalLoader, ModalHeader, ModalBody } from 'components/Modal'
import { formatDate } from 'helpers/formatDate'
import { getDefaultComputedFile } from 'helpers/getDefaultComputedFile'
import { hasMultiple } from 'helpers/hasMultiple'
import { isProjectID } from 'helpers/isProjectID'

// Button and Modal to show when downloading
export const Download = ({
  icon,
  resource: initialResource,
  publicComputedFile: initialPublicComputedFile
}) => {
  const { token, email, surveyListForm, createToken } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const [resource, setResource] = useState(initialResource)
  const [publicComputedFile, setPublicComputedFile] = useState(
    initialPublicComputedFile
  )
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const verb =
    download && token && publicComputedFile ? 'Downloading' : 'Download'
  const label = isProjectID(resource.scpca_id)
    ? `${verb} Project`
    : `${verb} Sample`

  const defaultComputedFile = getDefaultComputedFile(resource)

  const hasMultipleFiles = hasMultiple(resource.computed_files)

  const handleClick = () => {
    setShowing(true)
    if (download && download.download_url) {
      const { type, project, sample } = publicComputedFile
      trackDownload(type, project, sample)
      surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
      window.open(download.download_url)
    }
  }

  const handleBackToOptions = () => {
    setPublicComputedFile(null)
  }

  const handleSelectFile = (file, newResource) => {
    setDownload(false)
    if (resource) setResource(newResource)
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
    if (!showing) {
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
        surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
        window.open(downloadRequest.response.download_url)
        setDownload(downloadRequest.response)
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

    if (!download && token && showing && publicComputedFile) asyncFetch()
  }, [download, token, showing, publicComputedFile])

  return (
    <>
      {icon ? (
        <Anchor icon={icon} onClick={handleClick} />
      ) : (
        <Button
          aria-label={label}
          flex="grow"
          primary
          label={label}
          disabled={publicComputedFile === undefined}
          onClick={handleClick}
        />
      )}
      <Modal title={label} showing={showing} setShowing={setShowing}>
        {publicComputedFile &&
          hasMultipleFiles &&
          !initialPublicComputedFile && (
            <ModalHeader>
              <Text
                color="brand"
                role="button"
                margin={{ bottom: 'medium' }}
                style={{ cursor: 'pointer' }}
                onClick={handleBackToOptions}
              >
                <Icon size="16px" name="ChevronLeft" /> View Download Options
              </Text>
            </ModalHeader>
          )}
        <ModalBody>
          {download && token && publicComputedFile ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
              handleSelectFile={handleSelectFile}
            />
          ) : !token && publicComputedFile ? (
            <DownloadToken />
          ) : !publicComputedFile && hasMultipleFiles ? (
            <DownloadOptions
              resource={resource}
              handleSelectFile={handleSelectFile}
            />
          ) : (
            <ModalLoader />
          )}
        </ModalBody>
      </Modal>
    </>
  )
}

export default Download
