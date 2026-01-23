import React, { useEffect, useState } from 'react'
import { Box, Paragraph, Text } from 'grommet'
import { mapRowsWithColumns } from 'helpers/mapRowsWithColumns'
import { pluralizeCountText } from 'helpers/pluralizeCountText'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'

export const DatasetSummary = ({ dataset }) => {
  const [totalSample, setSampleTotal] = useState(0)
  const [totalProject, setTotalProject] = useState(0)

  const diagnosesSummary = dataset.diagnoses_summary
  const columns = ['Diagnosis', 'Samples', 'Projects']
  const data = mapRowsWithColumns(
    Object.entries(diagnosesSummary).map(
      ([diagnosis, { samples, projects }]) => [diagnosis, samples, projects]
    ),
    columns
  )

  useEffect(() => {
    setSampleTotal(dataset.total_sample_count || 0)
    setTotalProject(Object.keys(dataset.data).length || 0)
  }, [dataset])

  return (
    <Box>
      <Box
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
        gap="medium"
        margin={{ bottom: 'medium' }}
        pad={{ bottom: 'medium' }}
      >
        <Text serif size="large">
          Dataset Summary
        </Text>
        <Paragraph>
          <Text weight="bold">{pluralizeCountText(totalSample, 'Sample')}</Text>{' '}
          accross{' '}
          <Text weight="bold">
            {pluralizeCountText(totalProject, 'Project')}
          </Text>
        </Paragraph>
      </Box>
      <DatasetSummaryTable data={data} columns={columns} keyValue="Diagnosis" />
    </Box>
  )
}

export default DatasetSummary
