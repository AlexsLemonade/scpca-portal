import React from 'react'
import { Box } from 'grommet'
import { Table } from 'components/Table'
import samples from '../data/samples.js'

const columns = [
  { Header: 'Technologies', accessor: 'technologies' },
  { Header: 'Diagnosis', accessor: 'diagnosis' },
  { Header: 'Disease Timing', accessor: 'disease_timing' }
]

export default {
  title: 'Components/Table',
  args: { columns, data: samples }
}

export const Default = (args) => (
  <Box pad="xlarge">
    <Table {...args} />
  </Box>
)
