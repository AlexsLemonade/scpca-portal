import React from 'react'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

// This UI component is shown when all samples have been added to myDataset
export const DatasetAddProjectModalAddedContent = () => (
  <Box
    direction="row"
    align="center"
    gap="small"
    margin={{ vertical: 'small' }}
  >
    <Icon color="success" name="Check" />
    <Text color="success">Added to Dataset</Text>
  </Box>
)

export default DatasetAddProjectModalAddedContent
