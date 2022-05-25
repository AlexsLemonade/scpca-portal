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
      Cell: ({ row }) =>
        row.original.computed_file ? (
          <Box direction="row" gap="small" align="center">
            <Download
              Icon={<DownloadIcon color="brand" />}
              computedFile={row.original.computed_file}
            />
            <Text>{formatBytes(row.original.computed_file.size_in_bytes)}</Text>
          </Box>
        ) : (
          <Box width={{ min: '120px' }}>
            <Text>Not Available</Text>
            <Text>For Download</Text>
          </Box>
        )
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
    { Header: 'Treatment', accessor: ({ treatment }) => treatment || 'N/A' },
    { Header: 'Age at Diagnosis', accessor: 'age_at_diagnosis' },
    { Header: 'Sex', accessor: 'sex' },
    { Header: 'Sample Count Estimates', accessor: 'cell_count' },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    }
  ]

  React.useEffect(() => {
    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000 // TODO:: 'all' option
      })
      if (samplesRequest.isOk) {
        // if not all samples are downloadable show downloadable first
        const sortedSamples =
          project.sample_count !== project.downloadable_sample_count
            ? samplesRequest.response.results.sort(({ computed_file: a }) =>
                a && a.id ? -1 : 1
              )
            : samplesRequest.response.results
        setSamples(sortedSamples)
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
