import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { DatasetProjectAdditionalOptions } from 'components/DatasetProjectAdditionalOptions'
import { DatasetProjectModalityOptions } from 'components/DatasetProjectModalityOptions'
import { DatasetProjectDataFormat } from 'components/DatasetProjectDataFormat'
import { DatasetWarningSpatialSamples } from 'components/DatasetWarningSpatialSamples'
import { Modal, ModalBody } from 'components/Modal'

// Button and Modal to show when adding a project to My Dataset
// NOTE: All components accept a 'project' prop (for mock data) but it's subject to change
export const DatasetAddProjectModal = ({
  project,
  label = 'Add to Dataset',
  title = 'Add Project to Dataset',
  disabled = false
}) => {
  const { userFormat } = useScPCAPortal()
  const { myDataset, addProject, getProjectData } = useDatasetManager()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)
  const handleClick = () => {
    setShowing(true)
  }

  // Dataset attributes
  const [format, setFormat] = useState(myDataset.format || userFormat)
  const [modalities, setModalities] = useState([])
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)
  const [projectData, setProjectData] = useState({})

  const canAddProject = format && modalities.length > 0

  const singleCell = 'SINGLE_CELL'
  const spatial = 'SPATIAL'
  // TODO: Replace with actual stats value once ready
  const sampleDifferenceForSpatial = 5

  const handleAddProject = () => {
    addProject(project, format, projectData)
  }

  useEffect(() => {
    setProjectData({
      ...(modalities.includes(singleCell) &&
        getProjectData(project, singleCell, includeMerge)),
      ...(modalities.includes(spatial) &&
        getProjectData(project, spatial, false)), // Merge Spatial samples not supported
      includes_bulk: includeBulk
    })
  }, [modalities, includeBulk, includeMerge])

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
                <DatasetProjectDataFormat
                  project={project}
                  format={format}
                  handleSetFormat={setFormat}
                />
                <DatasetProjectModalityOptions
                  project={project}
                  format={format}
                  modalities={modalities}
                  handleSetModalities={setModalities}
                />
                <DatasetProjectAdditionalOptions
                  project={project}
                  format={format}
                  handleIncludeBulk={setIncludeBulk}
                  handleIncludeMerge={setIncludeMerge}
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
                  disabled={!canAddProject}
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
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetAddProjectModal
