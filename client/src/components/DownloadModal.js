/* eslint-disable no-nested-ternary */
import React, { useState } from 'react'
import { Anchor, Text } from 'grommet'
import { Button } from 'components/Button'
import { DownloadOptions } from 'components/DownloadOptions'
import { DownloadStarted } from 'components/DownloadStarted'
import { DownloadToken } from 'components/DownloadToken'
import { Icon } from 'components/Icon'
import { Modal, ModalLoader, ModalHeader, ModalBody } from 'components/Modal'
import { useDownloadModal } from 'hooks/useDownloadModal'

// Button and Modal to show when downloading
export const DownloadModal = ({
  label,
  resource: initialResource,
  publicComputedFile: initialPublicComputedFile,
  icon = null,
  disabled = false
}) => {
  const [showing, setShowing] = useState(false)
  const {
    handleSelectFile,
    modalTitle,
    tryDownload,
    publicComputedFile,
    setPublicComputedFile,
    hasDownloadOptions,
    download,
    resource,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  } = useDownloadModal(initialResource, initialPublicComputedFile, showing)
  const isDisabled = disabled || publicComputedFile === undefined

  const handleClick = () => {
    setShowing(true)
    // if they can just download, go straight there
    tryDownload()
  }

  // unselect the public computed file
  const handleBackToOptions = () => {
    setPublicComputedFile(null)
  }

  return (
    <>
      {icon ? (
        <Anchor
          icon={icon}
          onClick={handleClick}
          disabled={isDisabled}
          label={label}
        />
      ) : (
        <Button
          aria-label={label}
          flex="grow"
          primary
          label={label}
          disabled={isDisabled}
          onClick={handleClick}
        />
      )}
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        {hasDownloadOptions && (
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
          {isTokenReady ? (
            <DownloadToken resource={resource} />
          ) : isOptionsReady ? (
            <DownloadOptions
              resource={resource}
              handleSelectFile={handleSelectFile}
            />
          ) : isDownloadReady ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
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

export default DownloadModal
