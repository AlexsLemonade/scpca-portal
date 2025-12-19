import React, { useEffect, useState } from 'react'
import { Box, Paragraph } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { InfoViewMyDataset } from 'components/InfoViewMyDataset'

export const DatasetAddProjectModalRemainingContent = ({
  project,
  remainingSamples
}) => {
  const { myDataset, getDatasetProjectData } = useMyDataset()

  const [projectDataInMyDataset, setProjectDataInMyDataset] = useState(null)

  const addedSingleCellCount = projectDataInMyDataset?.SINGLE_CELL?.length
  const addedSpatialCount = projectDataInMyDataset?.SPATIAL?.length
  const addedSingleCellText =
    projectDataInMyDataset?.SINGLE_CELL === 'MERGED'
      ? 'All single-cell samples as a merged object'
      : `${
          remainingSamples?.SINGLE_CELL.length === 0 ? 'All' : ''
        } ${addedSingleCellCount} samples with single-cell modality`
  const addedSpatialText = `${
    remainingSamples?.SPATIAL.length === 0 ? 'All' : ''
  } ${addedSpatialCount} samples with spatial modality`

  //  Get the project data in myDataset for the Add Remaining state
  useEffect(() => {
    setProjectDataInMyDataset(getDatasetProjectData(project))
  }, [myDataset])

  return (
    <>
      <Box margin={{ vertical: 'medium' }}>
        <InfoViewMyDataset newTab />
      </Box>
      <Paragraph>You've already added the following to My Dataset:</Paragraph>
      <Box
        as="ul"
        margin={{ top: '0' }}
        pad={{ left: '26px' }}
        style={{ listStyle: 'disc' }}
      >
        {addedSingleCellCount > 0 && (
          <Box as="li" style={{ display: 'list-item' }}>
            {addedSingleCellText}
          </Box>
        )}

        {project.has_spatial_data && addedSpatialCount > 0 && (
          <Box as="li" style={{ display: 'list-item' }}>
            {addedSpatialText}
          </Box>
        )}

        {projectDataInMyDataset?.includes_bulk && (
          <Box as="li" style={{ display: 'list-item' }}>
            All bulk RNA-seq data in the project
          </Box>
        )}
      </Box>
    </>
  )
}

export default DatasetAddProjectModalRemainingContent
