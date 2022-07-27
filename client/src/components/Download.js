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
  const { token, email, surveyListForm } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const [resource, setResource] = useState(initialResource)
  const [recommendedResource, setRecommendedResource] = useState(null)
  const [publicComputedFile, setPublicComputedFile] = useState(null)
  const [initial, setInital] = useState(true)
  const [togglePublicComputedFile, setTogglePublicComputedFile] =
    useState(false)
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const label = isProjectID(resource.scpca_id)
    ? 'Download Project'
    : 'Download Sample'

  const defaultComputedFile = getDefaultComputedFile(resource)
  const multipleComputedFiles = hasMultiple(resource.computed_files)

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
        {publicComputedFile && multipleComputedFiles && (
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
              recommendedResource={recommendedResource}
              handleSelectFile={handleSelectFile}
              handleSelectRecommendedResource={handleSelectRecommendedResource}
            />
          ) : !token && publicComputedFile ? (
            <DownloadToken />
          ) : !publicComputedFile && multipleComputedFiles ? (
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
