import React, { useState } from 'react'
import { Anchor, Box, Grid, Heading } from 'grommet'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { useResponsive } from 'hooks/useResponsive'
import { AdditionalOptionsDataset } from 'components/AdditionalOptionsDataset'
import { Button } from 'components/Button'
import { CheckBoxGroupModalityDataset } from 'components/CheckBoxGroupModalityDataset'
import { Modal, ModalBody } from 'components/Modal'
import { SelectDataFormatDataset } from 'components/SelectDataFormatDataset'
import { WarningSpatialSamples } from 'components/WarningSpatialSamples'

// Button and Modal to show when adding a project to My Dataset
export const DatasetAddToModal = ({
  label = 'Add to Dataset',
  icon = null,
  disabled = false
}) => {
  const { responsive } = useResponsive()
  const { resourceType } = useDatasetOptionsContext()

  const buttonLabel = 'Add to Dataset'
  const modalTitle = `Add ${resourceType} to Dataset`

  const [showing, setShowing] = useState(false)

  const handleClick = () => {
    setShowing(true)
  }

  return (
    <>
      {icon ? (
        <Anchor
          icon={icon}
          onClick={handleClick}
          disabled={disabled}
          label={label}
        />
      ) : (
        <Button
          aria-label={label}
          flex="grow"
          primary
          label={label}
          disabled={disabled}
          onClick={handleClick}
        />
      )}
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
            <Heading level="3" size="small">
              Download Options
            </Heading>
            <Box pad={{ top: 'large' }}>
              <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                <SelectDataFormatDataset />
                <CheckBoxGroupModalityDataset />
                <AdditionalOptionsDataset />
              </Box>
              <Box
                align="center"
                direction={responsive('column', 'row')}
                gap="xlarge"
              >
                <Button primary aria-label={buttonLabel} label={buttonLabel} />
                <WarningSpatialSamples />
              </Box>
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetAddToModal
