/* eslint-disable no-nested-ternary */
import React, { useEffect, useState } from 'react'
import { useAnalytics } from 'hooks/useAnalytics'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadToken } from 'components/DownloadToken'
import { Icon } from 'components/Icon'
import { Modal, ModalHeader, ModalBody } from 'components/Modal'
import { formatDate } from 'helpers/formatDate'
import { getProjectID } from 'helpers/getProjectID'
import { hasMultiple } from 'helpers/hasMultiple'
import { hasToggleFile } from 'helpers/hasToggleFile'
import { isProjectID } from 'helpers/isProjectID'

// Button and Modal to show when downloading
export const Download = ({ icon, resource: initialResource }) => {
  const [resource, setResource] = useState(initialResource)
  const [project, setProject] = useState(null)
  const [initial, setInital] = useState(true)
  const [toggleFile, setToggleFile] = useState(false)
  const { token, email, surveyListForm } = useScPCAPortal()
  const { trackDownload } = useAnalytics()
  const [publicComputedFile, setPublicComputedFile] = useState(null)
  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const label = isProjectID(resource.scpca_id)
    ? 'Download Project'
    : 'Download Sample'
  const mutltipleComputedFiles = hasMultiple(resource.computed_files)

  const handleClick = () => {
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

  const handleToggleFile = () => {
    setResource(project)
    setPublicComputedFile(project.computed_files[0])
    setProject(null)
    setToggleFile(true)
    setInital(false)
    setDownload(false)
  }

  useEffect(() => {
    if (initial || (!initial && !toggleFile)) setResource(initialResource)

    setPublicComputedFile(
      mutltipleComputedFiles ? null : resource.computed_files[0]
    )

    const shouldFetchProject =
      publicComputedFile && hasToggleFile(publicComputedFile.type)

    const fetchProject = async () => {
      const { isOk, response } = await api.projects.get(
        getProjectID(resource.project)
      )
      if (isOk) {
        setProject(response)
      }
    }

    if (shouldFetchProject) fetchProject()
    setToggleFile(false)
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
        {publicComputedFile && mutltipleComputedFiles && (
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
              hasToggleFile={
                project
                  ? {
                      handleToggleFile,
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
    </>
  )
}

export default Download
