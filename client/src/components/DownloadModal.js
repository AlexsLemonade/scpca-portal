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
  icon,
  resource: initialResource,
  publicComputedFile: initialPublicComputedFile,
  disabled = false,
  sampleMetadataOnly = false // Optional prop to render metadata-only download button's label
}) => {
  const [showing, setShowing] = useState(false)
  const {
    handleSelectFile,
    modalTitle,
    buttonLabel,
    tryDownload,
    publicComputedFile,
    setPublicComputedFile,
    hasDownloadOptions,
    download,
    resource,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  } = useDownloadModal(
    initialResource,
    initialPublicComputedFile,
    showing,
    sampleMetadataOnly
  )

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
          disabled={disabled}
          label={
            sampleMetadataOnly ? <Text color="brand">{buttonLabel}</Text> : ''
          }
          margin={{ top: 'small' }}
        />
      ) : (
        <Button
          aria-label={buttonLabel}
          flex="grow"
          primary
          label={buttonLabel}
          disabled={publicComputedFile === undefined}
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
          {isDownloadReady ? (
            <DownloadStarted
              resource={resource}
              computedFile={download}
              handleSelectFile={handleSelectFile}
            />
          ) : isTokenReady ? (
            <DownloadToken />
          ) : isOptionsReady ? (
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

export default DownloadModal
