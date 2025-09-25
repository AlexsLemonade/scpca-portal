/* eslint-disable no-nested-ternary */
import React from 'react'
import { Button } from 'components/Button'
import { CCDLDatasetDownloadOptions } from 'components/CCDLDatasetDownloadOptions'
import { CCDLDatasetDownloadStarted } from 'components/CCDLDatasetDownloadStarted'
import { CCDLDatasetDownloadToken } from 'components/CCDLDatasetDownloadToken'
import { Modal, ModalLoader, ModalBody } from 'components/Modal'
import { useCCDLDatasetDownloadModal } from 'hooks/useCCDLDatasetDownloadModal'

export const CCDLDatasetDownloadModal = ({
  label,
  initialDatasets = [],
  disabled = false,
  white = false
}) => {
  const {
    showing,
    setShowing,
    modalTitle,
    datasets,
    setSelectedDataset,
    downloadDataset,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  } = useCCDLDatasetDownloadModal(initialDatasets)
  const isDisabled =
    disabled || !initialDatasets.some((dataset) => dataset.computed_file)

  const handleClick = () => {
    setShowing(true)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary={!white}
        label={label}
        disabled={isDisabled}
        onClick={handleClick}
      />
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          {isTokenReady ? (
            <CCDLDatasetDownloadToken />
          ) : isOptionsReady ? (
            <CCDLDatasetDownloadOptions
              datasets={datasets}
              handleSelectedDataset={setSelectedDataset}
            />
          ) : isDownloadReady ? (
            <CCDLDatasetDownloadStarted dataset={downloadDataset} />
          ) : (
            <ModalLoader />
          )}
        </ModalBody>
      </Modal>
    </>
  )
}

export default CCDLDatasetDownloadModal
