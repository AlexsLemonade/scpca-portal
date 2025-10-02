import React from 'react'
import { Box, Text } from 'grommet'
import { DatasetProjectCard } from 'components/DatasetProjectCard'

export const DatasetProjectSummary = ({ dataset, readOnly = false }) => (
  <Box margin={{ bottom: 'large' }}>
    <Box
      border={{ side: 'bottom', color: 'border-black', size: 'small' }}
      margin={{ bottom: 'medium' }}
      pad={{ bottom: 'small' }}
    >
      <Text serif size="large">
        Project Summary
      </Text>
    </Box>
    {Object.keys(dataset.data)
      .sort()
      .map((pId) => (
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

export default DatasetProjectSummary
