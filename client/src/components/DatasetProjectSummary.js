import React from 'react'
import { Box, Text } from 'grommet'
import { DatasetProjectCard } from 'components/DatasetProjectCard'
import { DatasetRemoveAllModal } from 'components/DatasetRemoveAllModal'

export const DatasetProjectSummary = ({ dataset, readOnly = false }) => {
  const projectKeys = Object.keys(dataset.data) || []

  return (
    <Box margin={{ bottom: 'large' }}>
      <Box
        direction="row"
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
        margin={{ bottom: 'medium' }}
        pad={{ bottom: 'small' }}
        justify="between"
      >
        <Text serif size="large">
          Project Summary
        </Text>
        {projectKeys.length > 1 && (
          <Box>
            <DatasetRemoveAllModal />
          </Box>
        )}
      </Box>
      {projectKeys.sort().map((pId) => (
        <Box margin={{ bottom: 'large' }} key={pId}>
          <DatasetProjectCard
            dataset={dataset}
            projectId={pId}
            readOnly={readOnly}
          />
        </Box>
      ))}
    </Box>
  )
}

export default DatasetProjectSummary
