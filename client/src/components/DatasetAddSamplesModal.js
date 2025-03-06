import React, { useState } from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { DatasetProjectDataFormat } from 'components/DatasetProjectDataFormat'
import { DatasetSamplesProjectOptions } from 'components/DatasetSamplesProjectOptions'

export const DatasetAddSamplesModal = ({
  label = 'Add to Dataset',
  title = 'Add Samples to Dataset',
  disabled = false
}) => {
  const { responsive } = useResponsive()
  const [showing, setShowing] = useState(false)

  const singleCellSamples = 8
  const spatialSamples = 4
  const totalSamples = singleCellSamples + spatialSamples

  const handleClick = () => {
    setShowing(true)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={disabled}
        onClick={handleClick}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid
            columns={['auto']}
            margin={{ bottom: '0' }}
            pad={{ bottom: '0' }}
          >
            <Box>
              <Paragraph margin={{ top: '0', bottom: '0' }}>
                Adding the following to Dataset:
              </Paragraph>
              <Paragraph
                margin={{ bottom: '0' }}
              >{`${totalSamples} samples`}</Paragraph>
              <Box
                as="ul"
                margin={{ top: '0' }}
                pad={{ left: '26px' }}
                style={{ listStyle: 'disc' }}
              >
                <Box as="li" style={{ display: 'list-item' }}>
                  {`${singleCellSamples} samples with single-cell modality`}
                </Box>
                <Box as="li" style={{ display: 'list-item' }}>
                  {`${spatialSamples} samples with spatial modality`}
                </Box>
              </Box>
            </Box>
            <Heading
              level="3"
              size="small"
              margin={{ top: '0', bottom: 'medium' }}
            >
              Additional Download Options
            </Heading>
            <Box pad={{ top: 'small' }}>
              <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                <DatasetProjectDataFormat />
                <DatasetSamplesProjectOptions />
              </Box>
              <Box
                align="center"
                direction={responsive('column', 'row')}
                gap="xlarge"
              >
                <Button primary aria-label={label} label={label} />
              </Box>
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}
