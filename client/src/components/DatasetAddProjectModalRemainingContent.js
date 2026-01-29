import React, { useEffect, useState } from 'react'
import { Box, Paragraph } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { InfoViewMyDataset } from 'components/InfoViewMyDataset'

// This UI component is only shown for the 'Add Remaining' button
// - Display the info message to view My Dataset
// - Display the already added samples in My Dataset
export const DatasetAddProjectModalRemainingContent = ({ project }) => {
  const {
    myDataset,
    getMyDatasetProjectData,
    hasMyDatasetAllProjectSamplesAdded
  } = useMyDataset()

  const [projectDataInMyDataset, setProjectDataInMyDataset] = useState(null)
  const [isAllSamplesAdded, setIsAllSamplesAdded] = useState(false)

  const addedSingleCellCount = projectDataInMyDataset?.SINGLE_CELL?.length
  const addedSpatialCount = projectDataInMyDataset?.SPATIAL?.length
  const addedSingleCellText =
    projectDataInMyDataset?.SINGLE_CELL === 'MERGED'
      ? 'All single-cell samples as a merged object'
      : `${
          isAllSamplesAdded ? 'All' : ''
        } ${addedSingleCellCount} samples with single-cell modality`
  const addedSpatialText = `${
    isAllSamplesAdded ? 'All' : ''
  } ${addedSpatialCount} samples with spatial modality`

  //  Get the project data in myDataset for the Add Remaining state
  useEffect(() => {
    setProjectDataInMyDataset(getMyDatasetProjectData(project))
    setIsAllSamplesAdded(hasMyDatasetAllProjectSamplesAdded(project))
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
