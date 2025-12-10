import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { api } from 'api'
import { Button } from 'components/Button'
import { InfoViewMyDataset } from 'components/InfoViewMyDataset'
import { DatasetProjectAdditionalOptions } from 'components/DatasetProjectAdditionalOptions'
import { DatasetProjectModalityOptions } from 'components/DatasetProjectModalityOptions'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetWarningMissingSamples } from 'components/DatasetWarningMissingSamples'
import { Modal, ModalBody, ModalLoader } from 'components/Modal'

export const DatasetAddRemainingModal = ({
  project,
  label = 'Add Remaining',
  title = 'Add Remaining Samples to Dataset',
  disabled = false
}) => {
  const {
    myDataset,
    defaultProjectOptions,
    userFormat,
    setUserFormat,
    getDatasetProjectData,
    getMissingModaliesSamples,
    addProject,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples,
    getRemainingProjectSampleIds
  } = useMyDataset()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)

  const [modalities, setModalities] = useState([])

  // For additional options
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  const [remainingSamples, setRemainingSamples] = useState(null)
  useEffect(() => {
    if (!samples.length) return
    setRemainingSamples(getRemainingProjectSampleIds(project, samples))
  }, [myDataset, samples])

  // For displaying the count of already added sample in the modal
  const [projectDataInMyDataset, setProjectDataInMyDataset] = useState(null)

  // For building the project data for the dataset
  const [projectData, setProjectData] = useState({})
  const [samples, setSamples] = useState(
    // We get either sample IDs (on Browse) or sample objects (on View Project)
    project.samples.filter((s) => s.scpca_id)
  )
  const [singleCellSamples, setSingleCellSamples] = useState([])
  const [spatialSamples, setSpatialSamples] = useState([])

  const [sampleDifference, setSampleDifference] = useState([])

  const addedSingleCellText =
    projectDataInMyDataset?.SINGLE_CELL === 'MERGED'
      ? 'All single-cell samples as a merged object'
      : `${remainingSamples?.SINGLE_CELL.length === 0 ? 'All' : ''} ${
          projectDataInMyDataset?.SINGLE_CELL.length
        } samples with single-cell modality`

  const addedSpatialText = `${
    remainingSamples?.SPATIAL.length === 0 ? 'All' : ''
  } ${projectDataInMyDataset?.SPATIAL?.length} samples with spatial modality`

  const canClickAddProject = modalities.length > 0

  const handleAddProject = async () => {
    await addProject(project, projectData, userFormat)
    setShowing(false)
  }

  // Set excludeMultiplexed based on userFormat
  useEffect(() => {
    // Multiplexed samples are not available for ANN_DATA
    setExcludeMultiplexed(userFormat === 'ANN_DATA')
  }, [userFormat])

  // Set default additional options based on project
  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project
  useEffect(() => {
    setIncludeBulk(hasBulkRnaSeq ? defaultProjectOptions.includeBulk : false)
    setIncludeMerge(
      includesMergedSce || includesMergedAnnData
        ? defaultProjectOptions.includeMerge
        : false
    )
    setModalities(
      getProjectModalities(project).filter((m) =>
        defaultProjectOptions.modalities.includes(m)
      )
    )
  }, [defaultProjectOptions])

  // Reset Data Fromat dropdown value on modal closes
  useEffect(() => {
    if (!myDataset.format) {
      setUserFormat(getProjectFormats(project)[0])
    } else {
      setUserFormat(myDataset.format)
    }
  }, [myDataset.format, showing])

  // Fetch samples list when modal opens via Browse page
  useEffect(() => {
    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000 // TODO:: 'all' option
      })

      if (samplesRequest.isOk) {
        setSamples(samplesRequest.response.results)
      }
    }
    if (!samples.length && showing) asyncFetch()
  }, [showing])

  // Get the project data in myDataset
  useEffect(() => {
    setProjectDataInMyDataset(getDatasetProjectData(project))
  }, [myDataset])

  // Populate the project data for addProject
  useEffect(() => {
    setProjectData({
      ...getProjectDataSamples(
        project,
        modalities,
        singleCellSamples,
        spatialSamples
      ),
      includes_bulk: includeBulk
    })
  }, [includeBulk, modalities, singleCellSamples, spatialSamples])

  // Update singleCellSamples based on user selections
  useEffect(() => {
    if (!projectDataInMyDataset) return

    if (modalities.includes('SINGLE_CELL')) {
      setSingleCellSamples(
        getProjectSingleCellSamples(samples, includeMerge, excludeMultiplexed)
      )
    } else {
      setSingleCellSamples(projectDataInMyDataset.SINGLE_CELL)
    }
  }, [excludeMultiplexed, includeMerge, modalities, samples])

  // Update spatialSamples based on user selections
  useEffect(() => {
    if (!projectDataInMyDataset) return

    if (modalities.includes('SPATIAL')) {
      setSpatialSamples(getProjectSpatialSamples(samples))
    } else {
      setSpatialSamples(projectDataInMyDataset.SPATIAL)
    }
  }, [modalities, samples])

  // Calculate missing modality samples
  useEffect(() => {
    setSampleDifference(getMissingModaliesSamples(samples, modalities))
  }, [modalities, samples])

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        secondary
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          {!samples.length ? (
            <ModalLoader />
          ) : (
            <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
              <Heading level="3" size="small" margin={{ top: '0' }}>
                Download Options
              </Heading>
              <Box margin={{ vertical: 'medium' }}>
                <InfoViewMyDataset newTab />
              </Box>
              <Paragraph>
                You've already added the following samples to My Dataset:
              </Paragraph>
              <Box
                as="ul"
                margin={{ top: '0' }}
                pad={{ left: '26px' }}
                style={{ listStyle: 'disc' }}
              >
                <Box as="li" style={{ display: 'list-item' }}>
                  {addedSingleCellText}
                </Box>
                {project.has_spatial_data && (
                  <Box as="li" style={{ display: 'list-item' }}>
                    {addedSpatialText}
                  </Box>
                )}
              </Box>
              <Box pad={{ top: 'large' }}>
                <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                  <DatasetDataFormatOptions project={project} />
                  <DatasetProjectModalityOptions
                    project={project}
                    remainingSamples={remainingSamples}
                    modalities={modalities}
                    onModalitiesChange={setModalities}
                  />
                  <DatasetProjectAdditionalOptions
                    project={project}
                    remainingSamples={remainingSamples}
                    selectedFormat={userFormat}
                    selectedModalities={modalities}
                    excludeMultiplexed={excludeMultiplexed}
                    includeBulk={includeBulk}
                    includeMerge={includeMerge}
                    onExcludeMultiplexedChange={setExcludeMultiplexed}
                    onIncludeBulkChange={setIncludeBulk}
                    onIncludeMergeChange={setIncludeMerge}
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
                    disabled={!canClickAddProject}
                    onClick={handleAddProject}
                  />
                  {sampleDifference.length > 0 && (
                    <DatasetWarningMissingSamples
                      project={project}
                      sampleCount={sampleDifference.length}
                    />
                  )}
                </Box>
              </Box>
            </Grid>
          )}
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetAddRemainingModal
