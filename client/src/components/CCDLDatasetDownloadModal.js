/* eslint-disable no-nested-ternary */
import React from 'react'
import { Anchor } from 'grommet'
import { Button } from 'components/Button'
import { CCDLDatasetDownloadOptions } from 'components/CCDLDatasetDownloadOptions'
import { CCDLDatasetDownloadStarted } from 'components/CCDLDatasetDownloadStarted'
import { CCDLDatasetDownloadToken } from 'components/CCDLDatasetDownloadToken'
import { Modal, ModalLoader, ModalBody } from 'components/Modal'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'

export const CCDLDatasetDownloadModal = ({
  label,
  icon = null,
  disabled = false,
  secondary = false
}) => {
  const {
    showing,
    setShowing,
    modalTitle,
    isDownloadReady,
    isTokenReady,
    isOptionsReady,
    datasets
  } = useCCDLDatasetDownloadModalContext()

  const isDisabled =
    disabled || !datasets?.some((dataset) => dataset.computed_file)

  const handleClick = () => {
    setShowing(true)
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
          primary={!secondary}
          label={label}
          disabled={isDisabled}
          onClick={handleClick}
        />
      )}
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          {isTokenReady ? (
            <CCDLDatasetDownloadToken />
          ) : isOptionsReady ? (
            <CCDLDatasetDownloadOptions />
          ) : isDownloadReady ? (
            <CCDLDatasetDownloadStarted />
          ) : (
            <ModalLoader />
          )}
        </ModalBody>
      </Modal>
    </>
  )
}

export default CCDLDatasetDownloadModal
