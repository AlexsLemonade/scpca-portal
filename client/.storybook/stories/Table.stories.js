import React from 'react'
import { Box } from 'grommet'
import { Table } from 'components/Table'
import project from 'data/project.json'

const columns = [
  { header: 'Technologies', accessorKey: 'technologies' },
  { header: 'Diagnosis', accessorKey: 'diagnosis' },
  { header: 'Disease Timing', accessorKey: 'disease_timing' }
]

export default {
  title: 'Components/Table',
  args: { columns, data: project.samples }
}

export const Default = (args) => (
  <Box pad="xlarge">
    <Table {...args} />
  </Box>
)
