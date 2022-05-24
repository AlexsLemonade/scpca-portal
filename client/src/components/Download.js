/* eslint-disable no-nested-ternary */
import React, { useContext, useEffect, useState } from 'react'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Modal, ModalHeader } from 'components/Modal'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadToken } from 'components/DownloadToken'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { AnalyticsContext } from 'contexts/AnalyticsContext'
import { api } from 'api'
import { formatDate } from 'helpers/formatDate'
import { isProjectID } from 'helpers/isProjectID'

// Button and Modal to show when downloading
export const Download = ({ icon, resource }) => {
  const { token, email, surveyListForm } = useContext(ScPCAPortalContext)
  const { trackDownload } = useContext(AnalyticsContext)
  const [publicComputedFile, setPublicComputedFile] = useState(() =>
    resource.computed_files.length === 1 ? resource.computed_files[0] : null
  )
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const label = isProjectID(resource.scpca_id)
    ? 'Download Project'
    : 'Download Sample'

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

  const handleSelectFile = (file) => {
    setDownload(false)
    setPublicComputedFile(file)
  }

  useEffect(() => {
    if (!showing) {
      setDownload(false)
      setPublicComputedFile(null)
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
      } else {
        console.error('clear the token and go back to that view')
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
        {publicComputedFile && (
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
        <Modal.Body>
          {download && token && publicComputedFile ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
              handleSelectFile={handleSelectFile}
            />
          ) : !token && publicComputedFile ? (
            <DownloadToken />
          ) : !publicComputedFile ? (
            <DownloadOptions
              handleSelectFile={handleSelectFile}
              computedFiles={resource.computed_files}
            />
          ) : null}
        </Modal.Body>
      </Modal>
    </>
  )
}

export default Download
