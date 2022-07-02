import React from 'react'
import { Table } from 'components/Table'

export const ProjectSamplesSummaryTable = ({ summaries }) => {
  const columns = [
    { Header: 'Diagnosis', accessor: 'diagnosis', isVisible: true },
    { Header: 'Sequencing Unit', accessor: 'seq_unit', isVisible: true },
    { Header: 'Technology', accessor: 'technology', isVisible: true },
    { Header: 'Library Count', accessor: 'sample_count', isVisible: true }
  ]
  return <Table columns={columns} data={summaries} />
}
