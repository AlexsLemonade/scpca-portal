import React, { useState } from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetSamplesProjectOptions } from 'components/DatasetSamplesProjectOptions'

export const DatasetAddSamplesModal = ({
  project,
  label = 'Add to Dataset',
  title = 'Add Samples to Dataset',
  disabled = false
}) => {
  const { setSamples } = useDatasetManager()
  const { selectedSamples } = useDatasetSamplesTable()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)

  // For project options
  const [includeBulk, setIncludeBulk] = useState(false)

  const singleCellSamples = selectedSamples?.SINGLE_CELL.length || 0
  const spatialSamples = selectedSamples?.SPATIAL.length || 0
  const totalSamples = singleCellSamples + spatialSamples

  const canClickAddSamples = totalSamples > 0

  const handleAddSamples = () => {
    setSamples(project, {
      ...selectedSamples,
      includes_bulk: includeBulk
    })
    setShowing(false)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid
            columns={['auto']}
            margin={{ bottom: '0' }}
            pad={{ bottom: '0' }}
          >
            <Box margin={{ bottom: 'medium' }}>
              <Paragraph margin={{ bottom: 'xsmall' }}>
                Adding the following to Dataset:
              </Paragraph>
              <Paragraph>{`${totalSamples} samples`}</Paragraph>
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
            <Heading level="3" size="small" margin={{ bottom: 'medium' }}>
              Additional Download Options
            </Heading>
            <Box pad={{ top: 'small' }}>
              <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                <DatasetDataFormatOptions project={project} />
                <DatasetSamplesProjectOptions
                  project={project}
                  includeBulk={includeBulk}
                  onIncludeBulkChange={setIncludeBulk}
                />
              </Box>
              <Box
                align="center"
                direction={responsive('column', 'row')}
                gap="xlarge"
              >
                <Button
                  primary
                  aria-label={label}
                  label={label}
                  disabled={!canClickAddSamples}
                  onClick={handleAddSamples}
                />
              </Box>
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}
