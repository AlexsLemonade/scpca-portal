import React from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { getReadable } from 'helpers/getReadable'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'
import { Link } from 'components/Link'

export const DatasetDownloadFileSummary = ({ dataset }) => {
  const filesSummary = dataset.stats.files_summary

  const columnOptions = [
    { label: 'Number of Samples', value: 'samples_count' },
    { label: 'Samples Modality', value: 'name' },
    { label: 'File Format', value: 'format' }
  ]

  const data = filesSummary.map((fs) =>
    columnOptions.reduce((acc, { label, value }) => {
      acc[label] = value === 'format' ? getReadable(fs[value]) : fs[value]
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
          Download File Summary
        </Text>
      </Box>
      <Box margin={{ bottom: 'medium' }}>
        <DatasetSummaryTable data={data} columns={columns} />
      </Box>
      <Link
        href={config.links.what_downloading}
        label="Learn more about download folder contents here."
      />
    </Box>
  )
}

export default DatasetDownloadFileSummary
