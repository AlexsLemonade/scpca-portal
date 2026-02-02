import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { differenceArray } from 'helpers/differenceArray'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { Button } from 'components/Button'
import { DatasetAddProjectModalRemainingContent } from 'components/DatasetAddProjectModalRemainingContent'
import { DatasetAddProjectModalAddedContent } from 'components/DatasetAddProjectModalAddedContent'
import { DatasetProjectAdditionalOptions } from 'components/DatasetProjectAdditionalOptions'
import { DatasetProjectModalityOptions } from 'components/DatasetProjectModalityOptions'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetWarningMissingSamples } from 'components/DatasetWarningMissingSamples'
import { Modal, ModalBody } from 'components/Modal'

// Three states: Add to Dataset (no samples added), Add Remaining (some samples added), Added to Dataset (all samples added)
export const DatasetAddProjectModal = ({ project, disabled = false }) => {
  const {
    myDataset,
    defaultProjectOptions,
    userFormat,
    setUserFormat,
    addProjectToMyDataset,
    hasMyDatasetAllProjectSamplesAdded,
    hasMyDatasetRemainingProjectSamples,
    getModalitySamplesDifference,
    getMyDatasetProjectData,
    getBuildMyDatasetProjectData
  } = useMyDataset()
  const { responsive } = useResponsive()

  const [showing, setShowing] = useState(false) // Modal toggle
  const [loading, setLoading] = useState(false)

  // For project options
  const [modalities, setModalities] = useState([])
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // For building the project data for adding to myDataset
  const [projectData, setProjectData] = useState({})
  const [singleCellSamples, setSingleCellSamples] = useState([])
  const [spatialSamples, setSpatialSamples] = useState([])

  const [sampleDifference, setSampleDifference] = useState([])

  // For the button states
  const [myDatasetProjectData, setMyDatasetProjectData] = useState(null)
  const [hasRemainingSamples, setHasRemainingSamples] = useState(false)
  const [isAllSamplesAdded, setIsAllSamplesAdded] = useState(false)

  const btnLabel = hasRemainingSamples ? 'Add Remaining' : 'Add to Dataset'
  const modalTitle = hasRemainingSamples
    ? 'Add Remaining Samples to Dataset'
    : 'Add Project to Dataset'

  const canClickAddProject = modalities.length > 0

  const handleAddProject = async () => {
    setLoading(true)
    await addProjectToMyDataset(project, projectData, userFormat)
    setLoading(false)
    setShowing(false)
  }

  // Set excludeMultiplexed based on userFormat
  useEffect(() => {
    // Multiplexed samples are not available for ANN_DATA
    setExcludeMultiplexed(userFormat === 'ANN_DATA')
  }, [userFormat])

  // Set default additional options based on project
  useEffect(() => {
    const bulkValue =
      myDatasetProjectData?.includes_bulk || defaultProjectOptions.includeBulk
    setIncludeBulk(project.has_bulk_rna_seq ? bulkValue : false)

    const mergedValue =
      myDatasetProjectData?.SINGLE_CELL === 'MERGED' ||
      defaultProjectOptions.includeMerge
    setIncludeMerge(
      project.includes_merged_sce || project.includes_merged_anndata
        ? mergedValue
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

  useEffect(() => {
    setMyDatasetProjectData(getMyDatasetProjectData(project))
    setHasRemainingSamples(hasMyDatasetRemainingProjectSamples(project))
    setIsAllSamplesAdded(hasMyDatasetAllProjectSamplesAdded(project))
  }, [myDataset])

  // Populate the project data for API call via addProjectToMyDataset
  useEffect(() => {
    setProjectData({
      ...getBuildMyDatasetProjectData(
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
    let projectSamples

    if (modalities.includes('SINGLE_CELL')) {
      if (includeMerge) {
        projectSamples = 'MERGED'
      } else {
        projectSamples = project.modality_samples.SINGLE_CELL

        if (excludeMultiplexed) {
          projectSamples = differenceArray(
            projectSamples,
            project.multiplexed_samples
          )
        }
      }
    } else {
      projectSamples = myDatasetProjectData?.SINGLE_CELL || []
    }

    setSingleCellSamples(projectSamples)
  }, [excludeMultiplexed, includeMerge, modalities, myDatasetProjectData])

  // Update spatialSamples based on user selections
  useEffect(() => {
    let projectSamples

    if (modalities.includes('SPATIAL')) {
      projectSamples = project.modality_samples.SPATIAL
    } else {
      projectSamples = myDatasetProjectData?.SPATIAL || []
    }

    setSpatialSamples(projectSamples)
  }, [modalities, myDatasetProjectData])

  // Calculate missing modality samples
  useEffect(() => {
    setSampleDifference(getModalitySamplesDifference(project, modalities))
  }, [modalities])

  if (isAllSamplesAdded) {
    return <DatasetAddProjectModalAddedContent />
  }

  return (
    <>
      <Button
        aria-label={btnLabel}
        flex="grow"
        primary={!hasRemainingSamples}
        secondary={hasRemainingSamples}
        label={btnLabel}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
            <Heading level="3" size="small" margin={{ top: '0' }}>
              Download Options
            </Heading>
            {myDataset.data?.[project.scpca_id] && (
              <DatasetAddProjectModalRemainingContent project={project} />
            )}
            <Box pad={{ top: 'large' }}>
              <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                <DatasetDataFormatOptions project={project} />
                <DatasetProjectModalityOptions
                  project={project}
                  modalities={modalities}
                  onModalitiesChange={setModalities}
                />
                <DatasetProjectAdditionalOptions
                  project={project}
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
                  aria-label={btnLabel}
                  label={btnLabel}
                  loading={loading}
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
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetAddProjectModal
