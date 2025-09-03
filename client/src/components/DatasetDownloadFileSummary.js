import React from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { getReadable } from 'helpers/getReadable'
import { mapRowsWithColumns } from 'helpers/mapRowsWithColumns'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'
import { Link } from 'components/Link'

export const DatasetDownloadFileSummary = ({ dataset }) => {
  const filesSummary = dataset.stats.files_summary

  const columns = ['Number of Samples', 'Samples Modality', 'File Format']

  const data = mapRowsWithColumns(
    filesSummary.map((fs) => [
      fs.samples_count,
      fs.name,
      getReadable(fs.format)
    ]),
    columns
  )

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
        <DatasetSummaryTable
          data={data}
          columns={columns}
          keyValue="Samples Modality"
        />
      </Box>
      <Link
        href={config.links.what_downloading}
        label="Learn more about download folder contents here."
      />
    </Box>
  )
}

export default DatasetDownloadFileSummary
