import React from 'react'
import { Table } from 'components/Table'

export const ProjectSamplesSummaryTable = ({ summaries }) => {
  const columns = [
    { header: 'Diagnosis', accessorKey: 'diagnosis' },
    { header: 'Sequencing Unit', accessorKey: 'seq_unit' },
    { header: 'Technology', accessorKey: 'technology' },
    { header: 'Library Count', accessorKey: 'sample_count' }
  ]
  return <Table columns={columns} data={summaries} />
}
