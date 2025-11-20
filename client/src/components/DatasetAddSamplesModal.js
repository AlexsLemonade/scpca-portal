import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { differenceArray } from 'helpers/differenceArray'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetSamplesProjectOptions } from 'components/DatasetSamplesProjectOptions'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const DatasetAddSamplesModal = ({
  project,
  samples,
  label = 'Add to Dataset',
  title = 'Add Samples to Dataset',
  disabled = false
}) => {
  const {
    myDataset,
    getDatasetProjectDataSamples,
    setSamples,
    userFormat,
    setUserFormat
  } = useMyDataset()
  const {
    canAddMultiplexed,
    showWarningMultiplexed,
    selectedSamples,
    setSelectedSamples
  } = useProjectSamplesTable()
  const { responsive } = useResponsive()

  const [selectedSingleCellSamples, setSelectedSingleCellSamples] = useState([])

  // Exclude multiplexed samples from selectedSamples for ANN_DATA
  // NOTE: Make sure not to lose the user's selection when toggling formats before API request
  useEffect(() => {
    if (!samples) return
    if (!project.has_multiplexed_data) {
      setSelectedSingleCellSamples(selectedSamples.SINGLE_CELL)
    } else {
      setSelectedSingleCellSamples(
        canAddMultiplexed
          ? selectedSamples.SINGLE_CELL
          : samples
              .filter(
                (s) =>
                  !s.has_multiplexed_data &&
                  selectedSamples.SINGLE_CELL.includes(s.scpca_id)
              )
              .map((s) => s.scpca_id)
      )
    }
  }, [userFormat, canAddMultiplexed, selectedSamples])

  // Modal toggle
  const [showing, setShowing] = useState(false)

  // For project options
  const [includeBulk, setIncludeBulk] = useState(false)

  // For counts of to-be-added samples in the modal
  const [singleCellSamplesToAdd, setSingleCellSamplesToAdd] = useState([])
  const [spatialSamplesToAdd, setSpatialSamplesToAdd] = useState([])

  // For the modal UI
  const totalSamples = singleCellSamplesToAdd + spatialSamplesToAdd
  const canClickAddSamples = totalSamples > 0

  const handleAddSamples = async () => {
    await setSamples(
      project,
      {
        ...selectedSamples,
        SINGLE_CELL: selectedSingleCellSamples,
        includes_bulk: includeBulk
      },
      userFormat
    )
    setShowing(false)
    // Refresh the table data
    setSelectedSamples((prev) => ({
      ...prev,
      SINGLE_CELL: selectedSingleCellSamples
    }))
  }

  // Reset Data Fromat dropdown value on modal closes
  useEffect(() => {
    if (!myDataset.format) {
      setUserFormat(getProjectFormats(project)[0])
    } else {
      setUserFormat(myDataset.format)
    }
  }, [myDataset.format, showing])

  // Calculate to-be-added samples for each modality
  useEffect(() => {
    if (samples) {
      const { SINGLE_CELL: singleCellSamples, SPATIAL: spatialSamples } =
        getDatasetProjectDataSamples(project, samples)

      setSingleCellSamplesToAdd(
        differenceArray(selectedSingleCellSamples, singleCellSamples).length ||
          0
      )
      setSpatialSamplesToAdd(
        differenceArray(selectedSamples.SPATIAL, spatialSamples).length || 0
      )
    }
  }, [
    userFormat,
    canAddMultiplexed,
    selectedSingleCellSamples,
    samples,
    selectedSamples
  ])

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
              {showWarningMultiplexed && !myDataset.format && (
                <Text margin={{ top: 'small' }}>
                  (*Multiplexed samples are excluded.)
                </Text>
              )}
            </Box>
            <Heading level="3" size="small" margin={{ bottom: 'medium' }}>
              Additional Download Options
            </Heading>
            <Box pad={{ top: 'small' }}>
              <Box pad={{ bottom: 'medium' }} width="680px">
                <Box margin={{ bottom: 'medium' }}>
                  <DatasetDataFormatOptions project={project} />
                  {showWarningMultiplexed && <WarningAnnDataMultiplexed />}
                </Box>
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
