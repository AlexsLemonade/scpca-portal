import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'
import { differenceArray } from 'helpers/differenceArray'
import { Button } from 'components/Button'
import { DatasetProjectAdditionalOptions } from 'components/DatasetProjectAdditionalOptions'
import { DatasetProjectModalityOptions } from 'components/DatasetProjectModalityOptions'
import { DatasetProjectDataFormat } from 'components/DatasetProjectDataFormat'
import { DatasetWarningSpatialSamples } from 'components/DatasetWarningSpatialSamples'
import { Modal, ModalBody, ModalLoader } from 'components/Modal'

// Button and Modal to show when adding a project to My Dataset
// NOTE: All components accept a 'project' prop (for mock data) but it's subject to change
export const DatasetAddProjectModal = ({
  project,
  label = 'Add to Dataset',
  title = 'Add Project to Dataset',
  disabled = false
}) => {
  const {
    addProject,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples
  } = useDatasetManager()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)

  const [modalities, setModalities] = useState([])
  // For additional options
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // For building the project data for the dataset
  const [projectData, setProjectData] = useState({})
  const [samples, setSamples] = useState(
    // We get either sample IDs (on Browse) or sample objects (on View Project)
    project.samples.filter((s) => s.scpca_id)
  )
  const [singleCellSamples, setSingleCellSamples] = useState([])
  const [spatialSamples, setSpatialSamples] = useState([])

  // TODO: Replace with actual stats value once ready
  // For SPATAIL modality only
  const allSingleCellSamples = getProjectSingleCellSamples(samples)
  const allSpatialSamples = getProjectSpatialSamples(samples)
  const sampleDifferenceForSpatial = [
    ...differenceArray(allSingleCellSamples, allSpatialSamples),
    ...differenceArray(allSpatialSamples, allSingleCellSamples)
  ].length

  const canClickAddProject = modalities.length > 0

  const handleAddProject = () => {
    addProject(project, projectData)
    setShowing(false)
  }

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
    if (modalities.includes('SINGLE_CELL')) {
      setSingleCellSamples(
        getProjectSingleCellSamples(samples, includeMerge, excludeMultiplexed)
      )
    } else {
      setSingleCellSamples([])
    }
  }, [excludeMultiplexed, includeMerge, modalities])

  // Update spatialSamples based on user selections
  useEffect(() => {
    if (modalities.includes('SPATIAL')) {
      setSpatialSamples(getProjectSpatialSamples(samples))
    } else {
      setSpatialSamples([])
    }
  }, [modalities])

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
          {!samples.length ? (
            <ModalLoader />
          ) : (
            <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
              <Heading
                level="3"
                size="small"
                margin={{ top: '0', bottom: 'medium' }}
              >
                Download Options
              </Heading>
              <Box pad={{ top: 'small' }}>
                <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                  <DatasetProjectDataFormat project={project} />
                  <DatasetProjectModalityOptions
                    project={project}
                    modalities={modalities}
                    onModalitiesChange={setModalities}
                  />
                  <DatasetProjectAdditionalOptions
                    project={project}
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
                  {project.has_spatial_data && (
                    <DatasetWarningSpatialSamples
                      sampleCount={sampleDifferenceForSpatial}
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

export default DatasetAddProjectModal
