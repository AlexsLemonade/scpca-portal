import React from 'react'
import { Table } from 'components/Table'

export const ProjectSamplesSummaryTable = ({ summaries }) => {
  const columns = [
    { Header: 'Diagnosis', accessor: 'diagnosis' },
    { Header: 'Sequencing Unit', accessor: 'seq_unit' },
    { Header: 'Technology', accessor: 'technology' },
    { Header: 'Library Count', accessor: 'sample_count' }
  ]
  return <Table columns={columns} data={summaries} />
}
