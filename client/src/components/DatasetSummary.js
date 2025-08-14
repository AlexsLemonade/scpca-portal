import React from 'react'
import { Box, Text } from 'grommet'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'

export const DatasetSummary = ({ dataset }) => {
  const diagnosesSummary = dataset.stats.diagnoses_summary

  const columnOptions = [
    { label: 'Diagnosis', value: 'diagnosis' },
    { label: 'Samples', value: 'samples' },
    { label: 'Projects', value: 'projects' }
  ]

  const data = Object.entries(diagnosesSummary).map(([diagnosis, counts]) =>
    columnOptions.reduce((acc, { label, value }) => {
      acc[label] = value === 'diagnosis' ? diagnosis : counts[value]
      return acc
    }, {})
  )

  const columns = columnOptions.map((co) => co.label)

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
