/* eslint-disable no-nested-ternary */
import React, { useState } from 'react'
import { Button } from 'components/Button'
import { DownloadOptions } from 'components/DownloadOptions'
import { DatasetDownloadStarted } from 'components/DatasetDownloadStarted'
import { DatasetDownloadToken } from 'components/DatasetDownloadToken'
import { Modal, ModalLoader, ModalBody } from 'components/Modal'
import { useCCDLDatasetDownloadModal } from 'hooks/useCCDLDatasetDownloadModal'

export const CCDLDatasetDownloadModal = ({
  label,
  initialDatasets,
  disabled = false
}) => {
  const [showing, setShowing] = useState(false)
  const {
    modalTitle,
    tryDownload,
    datasets,
    setSelectedDataset,
    downloadDataset,
    isDownloadReady,
    isTokenReady,
    isOptionsReady
  } = useCCDLDatasetDownloadModal(initialDatasets, showing)
  const isDisabled = disabled || !initialDatasets

  const handleClick = () => {
    setShowing(true)
    // try directly downloading from here
    tryDownload()
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={isDisabled}
        onClick={handleClick}
      />
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          {isTokenReady ? (
            <DatasetDownloadToken />
          ) : isOptionsReady ? (
            // this component is a placeholderwill
            // it will be replaced with CCDLDatasetDownloadOptions
            <DownloadOptions
              datasets={datasets}
              handleSelectedDataset={setSelectedDataset}
            />
          ) : isDownloadReady ? (
            <DatasetDownloadStarted dataset={downloadDataset} />
          ) : (
            <ModalLoader />
          )}
        </ModalBody>
      </Modal>
    </>
  )
}

export default CCDLDatasetDownloadModal
