import React from 'react'
import { Box, Text } from 'grommet'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'

export const DatasetSummary = ({ dataset }) => {
  const diagnosesSummary = dataset.stats.diagnoses_summary

  const columns = ['Diagnosis', 'Samples', 'Projects']

  const data = Object.entries(diagnosesSummary)
    .map(([diagnosis, { samples, projects }]) => [diagnosis, samples, projects])
    .map((row) =>
      Object.fromEntries(row.map((value, i) => [columns[i], value]))
    )

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
