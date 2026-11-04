import React from 'react'
import { getReadable } from 'helpers/getReadable'
import { Table } from 'components/Table'

export const ProjectSamplesSummaryTable = ({ summaries }) => {
  const columns = [
    { header: 'Diagnosis', accessorKey: 'diagnosis' },
    { header: 'Sequencing Unit', accessorKey: 'seq_unit' },
    { header: 'Technology', accessorKey: 'technology' },
    { header: 'Library Count', accessorKey: 'sample_count' }
  ]

  // Make sure the value of technology is human-readable
  const data = summaries.map((summary) => ({
    ...summary,
    technology: getReadable(summary.technology)
  }))

  return <Table columns={columns} data={data} />
}
