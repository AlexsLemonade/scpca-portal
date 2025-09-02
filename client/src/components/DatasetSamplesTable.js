import React from 'react'
import { config } from 'config'
import { Box, Text } from 'grommet'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { ModalityCheckBox } from 'components/ModalityCheckBox'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { Loader } from 'components/Loader'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { TriStateModalityCheckBoxHeader } from 'components/TriStateModalityCheckBoxHeader'

export const DatasetSamplesTable = ({
  project,
  samples,
  stickies = 3,
  editable = false
}) => {
  const { selectedSamples, setAllSamples, setFilteredSamples, toggleSample } =
    useDatasetSamplesTable()

  const hasMultiplexedData = project.has_multiplexed_data

  const text = 'Uncheck to change or remove modality'

  const availableModalities = [
    { key: 'SINGLE_CELL', value: project.has_single_cell_data },
    { key: 'SPATIAL', value: project.has_spatial_data }
  ]
    .filter((m) => m.value)
    .map((m) => m.key)
  const checkBoxCellWidth = availableModalities.length > 1 ? '200px' : '50px'

  const columns = [
    {
      Header: (
        <Box width={checkBoxCellWidth}>
          <TriStateModalityCheckBoxHeader
            project={project}
            modalities={availableModalities}
            editable={editable}
          />
        </Box>
      ),
      disableSortBy: true,
      accessor: 'data',
      Cell: ({ row }) => (
        <Box
          align="center"
          direction="row"
          justify="around"
          width={checkBoxCellWidth}
        >
          {availableModalities.map((m) => (
            <ModalityCheckBox
              key={`${row.original.scpca_id}_${m}`}
              project={project}
              modality={m}
              samples={samples}
              sampleId={row.original.scpca_id}
              disabled={!row.original[`has_${m.toLowerCase()}_data`]}
              editable={editable}
              onClick={() => toggleSample(m, row.original)}
            />
          ))}
        </Box>
      )
    },
    {
      Header: 'Sample ID',
      accessor: 'scpca_id',
      Cell: ({ row }) => (
        <Box>
          <Text>{row.original.scpca_id}</Text>
          {row.original.has_multiplexed_data && (
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
    {
      Header: 'Multiplexed with',
      accessor: 'multiplexed_with',
      Cell: ({
        row: {
          original: { multiplexed_with: multiplexedWith }
        }
      }) => (
        <Box width={{ max: '200px' }} style={{ whiteSpace: ' break-spaces' }}>
          {multiplexedWith.length ? multiplexedWith.join(', ') : 'N/A'}
        </Box>
      ),
      isVisible: hasMultiplexedData
    },
    {
      Header: 'Sequencing Units',
      accessor: 'seq_units',
      Cell: ({ row }) => <Text>{row.original.seq_units.join(', ')}</Text>
    },
    {
      Header: 'Technology',
      accessor: 'technologies',
      Cell: ({ row }) => <Text>{row.original.technologies.join(', ')}</Text>
    },
    {
      Header: 'Modalities',
      accessor: ({ modalities }) =>
        modalities.map(getReadableModality).join(', ')
    },
    { Header: 'Disease Timing', accessor: 'disease_timing' },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A'
    },
    {
      Header: 'Age',
      accessor: 'age'
    },
    {
      Header: 'Age Timing',
      accessor: 'age_timing'
    },
    { Header: 'Sex', accessor: 'sex' },
    {
      Header: 'Sample Count Estimates',
      accessor: ({ sample_cell_count_estimate: count }) => count || 'N/A'
    },
    {
      id: 'demux_cell_count_estimate_sum',
      Header: () => (
        <Box direction="row" align="center">
          Est. Demux Sample Counts&nbsp;
          <Link href={config.links.what_est_demux_cell}>
            <Icon size="small" name="Help" />
          </Link>
          &nbsp;&nbsp;
        </Box>
      ),
      accessor: ({ demux_cell_count_estimate_sum: count }) => count || 'N/A',
      isVisible: hasMultiplexedData
    },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    }
  ]

  if (!samples)
    return (
      <Box margin="64px">
        <Loader />
      </Box>
    )

  return (
    <Table
      columns={columns}
      data={samples}
      filter
      stickies={stickies}
      pageSize={5}
      pageSizeOptions={[5, 10, 20, 50]}
      text={<Text italic>{text}</Text>}
      defaultSort={[{ id: 'scpca_id', asc: true }]}
      selectedRows={selectedSamples}
      onAllRowsChange={setAllSamples}
      onFilteredRowsChange={setFilteredSamples}
    />
  )
}
