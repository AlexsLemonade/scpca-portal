/* eslint-disable no-nested-ternary */
import React, { useEffect, useState } from 'react'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Modal, ModalHeader, ModalBody } from 'components/Modal'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadToken } from 'components/DownloadToken'
import { useAnalytics } from 'hooks/useAnalytics'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { hasMultiple } from 'helpers/hasMultiple'
import { formatDate } from 'helpers/formatDate'
import { isProjectID } from 'helpers/isProjectID'
import { isMultiplexedSample } from 'helpers/isMultiplexedSample'
import { getProjectID } from 'helpers/getProjectID'

// Button and Modal to show when downloading
export const Download = ({ icon, resource: initialResource }) => {
  const [resource, setResource] = useState(initialResource)
  const [project, setProject] = useState(null)
  const { token, email, surveyListForm } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const mutltipleComputedFiles = hasMultiple(resource.computed_files)
  const [publicComputedFile, setPublicComputedFile] = useState(null)
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const label = isProjectID(resource.scpca_id)
    ? 'Download Project'
    : 'Download Sample'

  const handleClick = () => {
    // ! Temp - remove once the API is ready
    if (resource.scpca_id === 'SCPCP000009') {
      setPublicComputedFile(resource.computed_files[0])
    }

    setShowing(true)
    if (download && download.download_url) {
      const { type, project: projectID, sample } = publicComputedFile
      trackDownload(type, projectID, sample)
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

  // * ONLY multiplexed
  const handleDownloadProject = () => {
    setResource(project)
    setPublicComputedFile(project.computed_files[0])
    setProject(null)
    setDownload(false)
  }

  useEffect(() => {
    const newPublicComputedFile = mutltipleComputedFiles
      ? null
      : resource.computed_files[0]
    setPublicComputedFile(newPublicComputedFile)
    const shouldFetchProject =
      newPublicComputedFile && isMultiplexedSample(newPublicComputedFile.type)
    const fetchProject = async () => {
      const { isOk, response } = await api.projects.get(
        getProjectID(resource.project)
      )
      if (isOk) {
        // ! Temp - remove once the API is ready
        if (response && response.scpca_id === 'SCPCP000009') {
          // eslint-disable-next-line no-param-reassign
          response.has_multiplexed_data = true
          // eslint-disable-next-line no-param-reassign
          response.modalities = 'Multiplexed'
          // eslint-disable-next-line no-param-reassign
          response.computed_files = response.computed_files.filter(
            (c) => c.type !== 'PROJECT_ZIP'
          )
        }
        setProject(response)
      }
    }

    if (shouldFetchProject) fetchProject()
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
        const { type, project: projectID, sample } = publicComputedFile
        trackDownload(type, projectID, sample)
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
    <span>
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
        {publicComputedFile && hasMultiple(resource.computed_files) && (
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
              hasDownloadProject={
                project
                  ? {
                      handleDownloadProject,
                      projectSize: project.computed_files[0].size_in_bytes
                    }
                  : null
              }
            />
          ) : !token && publicComputedFile ? (
            <DownloadToken />
          ) : !publicComputedFile && mutltipleComputedFiles ? (
            <DownloadOptions
              resource={resource}
              handleSelectFile={handleSelectFile}
            />
          ) : null}
        </ModalBody>
      </Modal>
    </span>
  )
}

export default Download
