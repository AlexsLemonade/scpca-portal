import React from 'react'
import { api } from 'api'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { Download as DownloadIcon } from 'grommet-icons'
import { Download } from 'components/Download'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { accumulateValue } from 'helpers/accumulateValue'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'

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
      accessor: () => 'computed_files',
      Cell: ({ row }) =>
        row.original.computed_files.length !== 0 ? (
          <Box direction="row" gap="small" align="center">
            <Download
              icon={<DownloadIcon color="brand" />}
              resource={row.original}
            />
            <Text>
              {formatBytes(
                accumulateValue(row.original.computed_files, 'size_in_bytes')
              )}
            </Text>
          </Box>
        ) : (
          <Box width={{ min: '120px' }}>
            <Text>Not Available</Text>
            <Text>For Download</Text>
          </Box>
        )
    },
    {
      Header: 'Sample ID',
      accessor: ({ scpca_id: id, has_multiplexed_data: multiplexed }) => (
        <Box>
          <Text>{id}</Text>
          {multiplexed && (
            <Pill
              textSize="small"
              label={getReadable('has_multiplexed_data')}
              bullet={false}
            />
          )}
        </Box>
      )
    },
    {
      Header: 'Diagnosis - Subdiagnosis',
      accessor: ({ diagnosis, subdiagnosis }) => `${diagnosis} ${subdiagnosis}`,
      Cell: ({ row }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: 'normal' }}>
          <Text>{row.original.diagnosis}</Text>
          <Text size="small">{row.original.subdiagnosis}</Text>
        </Box>
      )
    },
    { Header: 'Sequencing Units', accessor: 'seq_units' },
    { Header: 'Technology', accessor: 'technologies' },
    {
      Header: 'Other Modalities',
      accessor: ({ modalities }) => modalities || 'N/A'
    },
    { Header: 'Disease Timing', accessor: 'disease_timing' },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A'
    },
    {
      Header: 'Age at Diagnosis',
      accessor: 'age_at_diagnosis'
    },
    { Header: 'Sex', accessor: 'sex' },
    {
      Header: 'Sample Count Estimates',
      accessor: ({ sample_cell_count_estimate: count }) => count || 'N/A'
    },
    {
      Header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessor: 'demux_cell_count_estimate',
      Cell: ({ demux_cell_count_estimate: count }) => count || 'N/A',
      isVisible: project.has_multiplexed_data
    },
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
            ? samplesRequest.response.results.sort(({ computed_files: a }) =>
                a && a.length ? -1 : 1
              )
            : samplesRequest.response.results
        setSamples(sortedSamples)
        setLoaded(true)
      }
    }
    if (!samples && !loaded) asyncFetch()
    if (samples && !loaded) setLoaded(true)
  }, [samples, loaded])

  if (!loaded)
    return (
      <Box margin="64px">
        <Loader />
      </Box>
    )
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
