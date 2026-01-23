import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
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
    getMyDatasetProjectDataSamples,
    setMyDatasetSamples,
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
  const [selectedMulstiplexedSamples, setSelectedMultiplexedSamples] = useState(
    []
  )
  // Exclude multiplexed samples from selectedSamples for ANN_DATA
  // NOTE: Make sure not to lose the user's selection when toggling formats before API request
  useEffect(() => {
    if (!samples) return

    if (!project.has_multiplexed_data || canAddMultiplexed) {
      setSelectedSingleCellSamples(selectedSamples.SINGLE_CELL)
      return
    }

    const selectedSet = new Set(selectedSamples.SINGLE_CELL)
    setSelectedSingleCellSamples(
      samples
        .filter((s) => !s.has_multiplexed_data && selectedSet.has(s.scpca_id))
        .map((s) => s.scpca_id)
    )
  }, [userFormat, canAddMultiplexed, selectedSamples])

  // Get multiplexed samples in selectedSamples
  useEffect(() => {
    if (!samples || !project.has_multiplexed_data) return

    const samplesSet = new Set(selectedSamples.SINGLE_CELL)
    setSelectedMultiplexedSamples(
      samples
        .filter((s) => s.has_multiplexed_data && samplesSet.has(s.scpca_id))
        .map((s) => s.scpca_id)
    )
  }, [userFormat, canAddMultiplexed, selectedSamples])

  // Modal toggle
  const [showing, setShowing] = useState(false)
  const [loading, setLoading] = useState(false)

  // For project options
  const [includeBulk, setIncludeBulk] = useState(false)

  // For counts of to-be-added samples in the modal
  const [singleCellSamplesToAdd, setSingleCellSamplesToAdd] = useState([])
  const [spatialSamplesToAdd, setSpatialSamplesToAdd] = useState([])

  // For the modal UI
  const totalSamples = singleCellSamplesToAdd + spatialSamplesToAdd
  const canClickAddSamples =
    userFormat === 'ANN_DATA'
      ? totalSamples - selectedMulstiplexedSamples.length > 0
      : totalSamples > 0

  const handleAddSamples = async () => {
    setLoading(true)
    // Ensure that the merged object is retained if present in myDataset
    const samplesToAdd =
      myDataset.data?.[project.scpca_id]?.SINGLE_CELL === 'MERGED'
        ? 'MERGED'
        : selectedSingleCellSamples

    await setMyDatasetSamples(
      project,
      {
        ...selectedSamples,
        SINGLE_CELL: samplesToAdd,
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
    setLoading(false)
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
        getMyDatasetProjectDataSamples(project)

      setSingleCellSamplesToAdd(
        differenceArray(selectedSamples.SINGLE_CELL, singleCellSamples)
          .length || 0
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

  useEffect(() => {
    setLoading(false)
  }, [showing])

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
                You have selected the following to add to My Dataset:
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
                {project.has_spatial_data && (
                  <Box as="li" style={{ display: 'list-item' }}>
                    {`${spatialSamplesToAdd} samples with spatial modality`}
                  </Box>
                )}
              </Box>
            </Box>
            <Heading level="3" size="small" margin={{ bottom: 'medium' }}>
              Additional Download Options
            </Heading>
            <Box pad={{ top: 'small' }}>
              <Box pad={{ bottom: 'medium' }} width="680px">
                <Box margin={{ bottom: 'medium' }}>
                  <DatasetDataFormatOptions project={project} />
                  {showWarningMultiplexed && (
                    <WarningAnnDataMultiplexed
                      count={selectedMulstiplexedSamples.length}
                    />
                  )}
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
                  loading={loading}
                />
              </Box>
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}
