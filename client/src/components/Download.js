/* eslint-disable no-nested-ternary */
import React, { useContext, useEffect, useState } from 'react'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Modal } from 'components/Modal'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadToken } from 'components/DownloadToken'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { AnalyticsContext } from 'contexts/AnalyticsContext'
import { api } from 'api'
import { formatDate } from 'helpers/formatDate'

// Button and Modal to show when downloading
export const Download = ({ icon, resource }) => {
  const { token, email, surveyListForm } = useContext(ScPCAPortalContext)
  const { trackDownload } = useContext(AnalyticsContext)
  const [publicComputedFile, setPublicComputedFile] = useState(null)
  const label =
    publicComputedFile?.project || null ? 'Download Project' : 'Download Sample'

  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const [showDownloadOptions, setShowDownloadOptions] = useState(true)

  const handleClick = () => {
    setShowing(true)
    if (download && download.download_url) {
      const { type, project, sample } = publicComputedFile
      trackDownload(type, project, sample)
      surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
      window.open(download.download_url)
    }
  }

  const backToDownloadOptions = () => {
    if (!download) {
      setPublicComputedFile(null)
    }
    setShowDownloadOptions(true)
  }

  const switchComputedFile = (computedFile) => {
    setPublicComputedFile(computedFile)
    // setShowDownloadOptions(false)
  }

  useEffect(() => {
    if (resource.computed_files.length === 1) {
      setPublicComputedFile(resource.computed_files[0])
    }
  }, [])

  // useEffect(() => {
  //   console.log(publicComputedFile)
  // }, [publicComputedFile])

  useEffect(() => {
    if (!showing && !download) {
      if (resource.computed_files.length > 1) {
        setPublicComputedFile(null)
      }
      setShowDownloadOptions(true)
    }
  }, [showing])

  useEffect(() => {
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

    if (!download && token && showing) asyncFetch()
  }, [download, token, showing])
  return (
    <>
      {icon ? (
        <Anchor icon={icon} onClick={handleClick} />
      ) : (
        <Button
          flex="grow"
          primary
          label={label}
          disabled={publicComputedFile === undefined}
          onClick={handleClick}
        />
      )}
      <Modal showing={showing} setShowing={setShowing}>
        {!showDownloadOptions && (
          <Modal.Header>
            <Text
              color="brand"
              role="button"
              margin={{ bottom: 'medium' }}
              style={{ cursor: 'pointer' }}
              onClick={backToDownloadOptions}
            >
              <Icon size="16px" name="ChevronLeft" /> View Download Options
            </Text>
          </Modal.Header>
        )}
        <Modal.Title>{label}</Modal.Title>
        <Modal.Body>
          {download && !showDownloadOptions ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
              switchComputedFile={switchComputedFile}
            />
          ) : !download && !showDownloadOptions ? (
            <DownloadToken />
          ) : showDownloadOptions ? (
            <DownloadOptions
              computedFiles={resource.computed_files}
              setShowDownloadOptions={setShowDownloadOptions}
              setPublicComputedFile={setPublicComputedFile}
            />
          ) : null}
        </Modal.Body>
      </Modal>
    </>
  )
}

export default Download
