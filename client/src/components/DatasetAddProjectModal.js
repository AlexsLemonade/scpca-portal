import React, { useState } from 'react'
import { Box, Grid, Heading } from 'grommet'
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
  const { responsive } = useResponsive()
  const { has_spatial_data: hasSpatialData } = project
  const sampleDifferenceForSpatial = 5
  const [showing, setShowing] = useState(false)

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
                <DatasetProjectModalityOptions project={project} />
                <DatasetProjectAdditionalOptions project={project} />
              </Box>
              <Box
                align="center"
                direction={responsive('column', 'row')}
                gap="xlarge"
              >
                <Button primary aria-label={label} label={label} />
                {hasSpatialData && (
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
