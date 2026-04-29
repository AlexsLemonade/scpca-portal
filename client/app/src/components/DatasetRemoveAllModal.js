import React, { useState } from 'react'
import { Box, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { WarningText } from 'components/WarningText'

export const DatasetRemoveAllModal = ({
  label = 'Remove All',
  title = 'Are you sure you want to remove all projects?',
  disabled = false
}) => {
  const { clearMyDataset } = useMyDataset()

  const [showing, setShowing] = useState(false)

  const [removing, setRemoving] = useState(false)
  const handleRemoveAll = async () => {
    setRemoving(true)
    await clearMyDataset()
    setRemoving(false)
    setShowing(false)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        danger
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal showing={showing} setShowing={setShowing}>
        <Box
          gridArea="title"
          width="full"
          height={{ min: 'min-content' }}
          pad="medium"
        >
          <WarningText
            lineBreak={false}
            iconMargin="0"
            iconSize="24px"
            margin={false}
          >
            <Text size="21px">{title}</Text>
          </WarningText>
        </Box>
        <ModalBody>
          <Box
            align="center"
            direction="row"
            gap="xlarge"
            justify="end"
            margin={{ top: 'small' }}
          >
            <Button
              aria-label="No, keep all projects"
              label="No, keep all projects"
              onClick={() => setShowing(false)}
            />
            <Button
              primary
              aria-label="Yes, remove all projects"
              label="Yes, remove all projects"
              loading={removing}
              onClick={handleRemoveAll}
            />
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetRemoveAllModal
