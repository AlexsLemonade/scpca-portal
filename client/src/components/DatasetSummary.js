import React from 'react'
import { Box, Text } from 'grommet'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'

export const DatasetSummary = ({ dataset }) => {
  const diagnosesSummary = dataset.stats.diagnoses_summary

  const data = Object.entries(diagnosesSummary).map(
    ([d, { samples, projects }]) => ({
      Diagnosis: d,
      Samples: samples,
      Projects: projects
    })
  )

  const columns = ['Diagnosis', 'Samples', 'Projects']

  return (
    <Box>
      <Box
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
        margin={{ bottom: 'medium' }}
        pad={{ bottom: 'small' }}
      >
        <Text serif size="large">
          Dataset Summary
        </Text>
      </Box>
      <DatasetSummaryTable data={data} columns={columns} />
    </Box>
  )
}

export default DatasetSummary
