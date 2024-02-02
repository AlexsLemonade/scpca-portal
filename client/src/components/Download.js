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
import { getProjectID } from 'helpers/getProjectID'
import { hasMultiple } from 'helpers/hasMultiple'
import { hasRecommendedResource } from 'helpers/hasRecommendedResource'
import { isProjectID } from 'helpers/isProjectID'

// Button and Modal to show when downloading
export const Download = ({ icon, resource: initialResource }) => {
  const { token, email, surveyListForm, createToken } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const [resource, setResource] = useState(initialResource)
  const [recommendedResource, setRecommendedResource] = useState(null)
  const [publicComputedFile, setPublicComputedFile] = useState(null)
  const [initial, setInital] = useState(true)
  const [togglePublicComputedFile, setTogglePublicComputedFile] =
    useState(false)
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const label = `Download${download ? 'ing' : ''} ${
    isProjectID(resource.scpca_id) ? 'Project' : 'Sample'
  }`
  const defaultComputedFile = getDefaultComputedFile(resource)
  const multipleComputedFiles = hasMultiple(resource.computed_files)
  const isDownloadStarted = download && token && publicComputedFile
  const isNoToken = !token && publicComputedFile
  const isDownloadFileHasNotSelected =
    !publicComputedFile && multipleComputedFiles
  const hasMultipleDownloadOptions = publicComputedFile && multipleComputedFiles

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
    setDownload(false)
    setPublicComputedFile(null)
  }

  const handleSelectFile = (file) => {
    setDownload(false)
    setPublicComputedFile(file)
  }

  const handleSelectRecommendedResource = () => {
    setResource(recommendedResource)
    setPublicComputedFile(getDefaultComputedFile(recommendedResource))
    setRecommendedResource(null)
    setTogglePublicComputedFile(true)
    setInital(false)
    setDownload(false)
  }

  useEffect(() => {
    if (initial || (!initial && !togglePublicComputedFile))
      setResource(initialResource)

    setPublicComputedFile(multipleComputedFiles ? null : defaultComputedFile)

    const shouldFetchProject =
      publicComputedFile && hasRecommendedResource(publicComputedFile.type)

    const fetchProject = async () => {
      const { isOk, response } = await api.projects.get(
        getProjectID(resource.project)
      )
      if (isOk) {
        setRecommendedResource(response)
      }
    }

    if (shouldFetchProject) fetchProject()
    setTogglePublicComputedFile(false)
  }, [resource, showing])

  useEffect(() => {
    if (!showing) {
      setDownload(false)
    }

    const shouldFetch = !download && token && showing && publicComputedFile

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

    if (shouldFetch) asyncFetch()
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
        {hasMultipleDownloadOptions && (
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
          {isDownloadStarted ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
              recommendedResource={recommendedResource}
              handleSelectFile={handleSelectFile}
              handleSelectRecommendedResource={handleSelectRecommendedResource}
            />
          ) : isNoToken ? (
            <DownloadToken />
          ) : isDownloadFileHasNotSelected ? (
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
