import React, { useEffect } from 'react'
import { Box, Text } from 'grommet'
import { Table } from 'components/Table'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'
import { api } from 'api'
import { Download as DownloadIcon } from 'grommet-icons'
import { Download } from 'components/Download'
import { Loader } from 'components/Loader'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Pill } from 'components/Pill'
import { accumulateValue } from 'helpers/accumulateValue'
import { config } from 'config'

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

  // ! Temp - remove once the API is ready
  useEffect(() => {
    if (project.scpca_id === 'SCPCP000009') {
      if (samples) {
        samples.forEach((s) => {
          // eslint-disable-next-line no-param-reassign
          s.has_multiplexed_data = true
        })
      }
    }
  }, [samples])

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
        ),
      isVisible: true
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
      ),
      isVisible: true
    },
    {
      Header: 'Diagnosis - Subdiagnosis',
      accessor: ({ diagnosis, subdiagnosis }) => `${diagnosis} ${subdiagnosis}`,
      Cell: ({ row }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: 'normal' }}>
          <Text>{row.original.diagnosis}</Text>
          <Text size="small">{row.original.subdiagnosis}</Text>
        </Box>
      ),
      isVisible: true
    },
    { Header: 'Sequencing Units', accessor: 'seq_units', isVisible: true },
    { Header: 'Technology', accessor: 'technologies', isVisible: true },
    {
      Header: 'Other Modalities',
      accessor: ({ modalities }) => modalities || 'N/A',
      isVisible: true
    },
    { Header: 'Disease Timing', accessor: 'disease_timing', isVisible: true },
    { Header: 'Tissue Location', accessor: 'tissue_location', isVisible: true },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A',
      isVisible: true
    },
    {
      Header: 'Age at Diagnosis',
      accessor: 'age_at_diagnosis',
      isVisible: true
    },
    { Header: 'Sex', accessor: 'sex', isVisible: true },
    {
      Header: 'Sample Count Estimates',
      accessor: ({ sample_cell_count_estimate: count }) => count || 'N/A',
      isVisible: true
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
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', '),
      isVisible: true
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
