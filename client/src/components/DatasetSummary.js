import React, { useEffect, useState } from 'react'
import { Box, Paragraph, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { mapRowsWithColumns } from 'helpers/mapRowsWithColumns'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'

export const DatasetSummary = ({ dataset }) => {
  const { myDataset } = useMyDataset()

  const [totalSample, setSampleTotal] = useState(0)
  const [totalProject, setTotalProject] = useState(0)
  const sampleTotalText = `${totalSample} Sample${totalSample > 1 ? 's' : ''}`
  const projectTotalText = `${totalProject} Project${
    totalProject > 1 ? 's' : ''
  }`

  const diagnosesSummary = dataset.diagnoses_summary
  const columns = ['Diagnosis', 'Samples', 'Projects']
  const data = mapRowsWithColumns(
    Object.entries(diagnosesSummary).map(
      ([diagnosis, { samples, projects }]) => [diagnosis, samples, projects]
    ),
    columns
  )

  useEffect(() => {
    setSampleTotal(myDataset.total_sample_count || 0)
    setTotalProject(Object.keys(myDataset.data).length || 0)
  }, [myDataset])

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
          <Text weight="bold">{sampleTotalText}</Text> accross{' '}
          <Text weight="bold">{projectTotalText}</Text>
        </Paragraph>
      </Box>
      <DatasetSummaryTable data={data} columns={columns} keyValue="Diagnosis" />
    </Box>
  )
}

export default DatasetSummary
