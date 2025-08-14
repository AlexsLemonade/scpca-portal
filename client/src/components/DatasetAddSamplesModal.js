import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { differenceArray } from 'helpers/differenceArray'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetSamplesProjectOptions } from 'components/DatasetSamplesProjectOptions'

export const DatasetAddSamplesModal = ({
  project,
  samples,
  label = 'Add to Dataset',
  title = 'Add Samples to Dataset',
  disabled = false
}) => {
  const { getDatasetData, getProjectSingleCellSamples, setSamples } =
    useDatasetManager()
  const { selectedSamples } = useDatasetSamplesTable()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)

  // For project options
  const [includeBulk, setIncludeBulk] = useState(false)

  // For counts of to-be-added samples in the modal
  const [singleCellSamplesToAdd, setSingleCellSamplesToAdd] = useState([])
  const [spatialSamplesToAdd, setSpatialSamplesToAdd] = useState([])

  const totalSamples = singleCellSamplesToAdd + spatialSamplesToAdd

  const canClickAddSamples = totalSamples > 0

  const handleAddSamples = () => {
    setSamples(project, {
      ...selectedSamples,
      includes_bulk: includeBulk
    })
    setShowing(false)
  }

  // Calculate to-be-added samples for each modality
  useEffect(() => {
    if (samples) {
      const datasetData = getDatasetData(project)

      const singleCellSamples =
        datasetData.SINGLE_CELL === 'MERGED'
          ? getProjectSingleCellSamples(samples)
          : datasetData.SINGLE_CELL || []
      const spatialSamples = datasetData.SPATIAL || []

      setSingleCellSamplesToAdd(
        differenceArray(selectedSamples?.SINGLE_CELL, singleCellSamples)
          .length || 0
      )
      setSpatialSamplesToAdd(
        differenceArray(selectedSamples?.SPATIAL, spatialSamples).length || 0
      )
    }
  }, [samples, selectedSamples])

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
                  {`${singleCellSamplesToAdd} samples with single-cell modality`}
                </Box>
                <Box as="li" style={{ display: 'list-item' }}>
                  {`${spatialSamplesToAdd} samples with spatial modality`}
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
