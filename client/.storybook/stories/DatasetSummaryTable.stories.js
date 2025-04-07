
import React from 'react'
import { Box } from 'grommet'
import { DatasetSummaryTable } from 'components/DatasetSummaryTable'


const data = [
  { 'Number of Samples/Project': 1, 'Samples/Project Modality': 'Single-cell samples', 'File Format': "SingleCellExperiment (.rds)" },
  { 'Number of Samples/Project': 2, 'Samples/Project Modality': 'Single-nucli samples', 'File Format': "SingleCellExperiment (.rds)"},
  { 'Number of Samples/Project': 3, 'Samples/Project Modality': 'Single-cell samples with CITE-seq', 'File Format': "SingleCellExperiment (.rds)"},
  { 'Number of Samples/Project': 4, 'Samples/Project Modality': 'Spatial samples', 'File Format': "Spatial Format" },
  { 'Number of Samples/Project': 5, 'Samples/Project Modality': 'Bulk-RNA seq projects', 'File Format': ".tsv" },
]

const columns = ['Number of Samples/Project', 'Samples/Project Modality', 'File Format']

export default {
  title: 'Components/DatasetSummaryTable',
  args: { data, columns }
}

export const Default = (args) => (
  <Box gap="medium" direction="row">
    <DatasetSummaryTable {...args} />
  </Box>
)
