import React from 'react'
import { Box, Text } from 'grommet'
import { Table } from 'components/Table'
import { formatBytes } from 'helpers/formatBytes'
import { api } from 'api'
import { Download as DownloadIcon } from 'grommet-icons'
import { Download } from 'components/Download'
import { Loader } from 'components/Loader'

export const ProjectSamplesTable = ({
  project,
  samples: defaultSamples,
  stickies = 3
}) => {
  const [samples, setSamples] = React.useState(defaultSamples)
  const [loaded, setLoaded] = React.useState(false)
  const infoText =
    project && project.has_bulk_rna_seq
      ? 'Bulk RNA-seq data available only when you download the entire project'
      : false

  const columns = [
    {
      Header: 'Download',
      accessor: () => 'computed_file',
      Cell: ({ row }) => (
        <Box direction="row" gap="small" align="center">
          <Download
            Icon={<DownloadIcon color="brand" />}
            computedFile={row.original.computed_file}
          />
          <Text>{formatBytes(row.original.computed_file.size_in_bytes)}</Text>
        </Box>
      ),
      disableSortBy: true
    },
    { Header: 'Sample ID', accessor: 'scpca_id' },
    {
      Header: 'Diagnosis - Subdiagnosis',
      accessor: ({ diagnosis, subdiagnosis }) => `${diagnosis} ${subdiagnosis}`,
      Cell: ({ row }) => (
        <Box width={{ max: '200px' }} style={{ 'white-space': 'normal' }}>
          <Text>{row.original.diagnosis}</Text>
          <Text size="small">{row.original.subdiagnosis}</Text>
        </Box>
      )
    },
    { Header: 'Sequencing Units', accessor: 'seq_units' },
    { Header: 'Technology', accessor: 'technologies' },
    { Header: 'Disease Timing', accessor: 'disease_timing' },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    { Header: 'Treatment', accessor: 'treatment' },
    { Header: 'Age at Diagnosis', accessor: 'age_at_diagnosis' },
    { Header: 'Sex', accessor: 'sex' },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    },
    { Header: 'Sample Count Estimates', accessor: 'cell_count' }
  ]

  React.useEffect(() => {
    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000 // TODO:: 'all' option
      })
      if (samplesRequest.isOk) {
        setSamples(samplesRequest.response.results)
        setLoaded(true)
      }
    }

    if (!samples && !loaded) asyncFetch()
    if (samples && !loaded) setLoaded(true)
  }, [samples, loaded])

  if (!loaded) return <Loader />
  return (
    <Table
      filter
      columns={columns}
      data={samples}
      stickies={stickies}
      pageSize={5}
      pageSizeOptions={[5, 10, 20, 50]}
      infoText={infoText}
    />
  )
}
