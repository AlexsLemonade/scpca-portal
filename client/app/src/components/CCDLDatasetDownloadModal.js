import React from 'react'
import { Anchor, Box } from 'grommet'
import { Button } from 'components/Button'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'
import { CCDLDatasetDownloadOptions } from 'components/CCDLDatasetDownloadOptions'
import { CCDLDatasetDownloadStarted } from 'components/CCDLDatasetDownloadStarted'
import { CCDLDatasetDownloadToken } from 'components/CCDLDatasetDownloadToken'
import { Modal, ModalLoader, ModalBody } from 'components/Modal'
import { WarningProjectOptionsUnavailable } from 'components/WarningProjectOptionsUnavailable'

const CCDLDatasetDownloadModalBody = () => {
  const { isDownloadReady, isTokenReady, isOptionsReady } =
    useCCDLDatasetDownloadModalContext()

  if (isTokenReady) return <CCDLDatasetDownloadToken />
  if (isOptionsReady) return <CCDLDatasetDownloadOptions />
  if (isDownloadReady) return <CCDLDatasetDownloadStarted />
  return <ModalLoader />
}

export const CCDLDatasetDownloadModal = ({
  label,
  icon = null,
  disabled = false,
  secondary = false
}) => {
  const { showing, setShowing, modalTitle, datasets, isInvalidCCDLName } =
    useCCDLDatasetDownloadModalContext()

  const isDisabled =
    disabled || !datasets.some((dataset) => dataset.computed_file)

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
          {isInvalidCCDLName && (
            <WarningProjectOptionsUnavailable
              text="Unable to prepopulate download options. Please select the correct dataset options."
              iconColor="error"
              iconMargin="none"
              iconName="WarningNoFill"
            />
          )}
          <CCDLDatasetDownloadModalBody />
        </ModalBody>
      </Modal>
    </>
  )
}

export default CCDLDatasetDownloadModal
