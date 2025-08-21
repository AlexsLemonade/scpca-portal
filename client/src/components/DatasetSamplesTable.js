import React from 'react'
import { Box, Text } from 'grommet'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { Button } from 'components/Button'
import { ModalityCheckBox } from 'components/ModalityCheckBox'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { TriStateModalityCheckBox } from 'components/TriStateModalityCheckBox'

// NOTE: This component accepts 'samples' prop but it's subject to change
// Currently mock data is used via Storybook for development
// Some cells are removed teemporarily (e.g., multiplexed only cells)
export const DatasetSamplesTable = ({ samples, stickies = 3 }) => {
  const { selectedSamples, toggleSample, setFilteredSamples } =
    useDatasetSamplesTable()

  const availableModalities = ['SINGLE_CELL', 'SPATIAL']
  const checkBoxCellWidth = '200px'

  const columns = [
    {
      Header: (
        <Box width={checkBoxCellWidth}>
          <Box align="center" margin={{ bottom: 'small' }} pad="small">
            Select Modality
          </Box>
          <Box
            border={{ side: 'bottom' }}
            width="100%"
            style={{ position: 'absolute', top: '45px', left: 0 }}
          />
          <Box direction="row" justify="around">
            {availableModalities.map((modality) => (
              <Box align="center" pad={{ horizontal: 'small' }}>
                <Text margin={{ bottom: 'xsmall' }}>
                  {getReadable(modality)}
                </Text>
                <TriStateModalityCheckBox modality={modality} />
              </Box>
            ))}
          </Box>
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
          {availableModalities.map((modality) => (
            <ModalityCheckBox
              modality={modality}
              sampleId={row.original.scpca_id}
              disabled={!row.original.data[modality].length}
              onClick={() => toggleSample(modality, row.original)}
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
      Header: 'Sequencing Units',
      accessor: 'seq_units',
      Cell: ({ row }) => <Text>{row.original.seq_units.join(', ')}</Text>
    },
    {
      Header: 'Modalities',
      accessor: ({ modalities }) =>
        modalities.map(getReadableModality).join(', ')
    },
    { Header: 'Tissue Location', accessor: 'tissue_location' },
    {
      Header: 'Treatment',
      accessor: ({ treatment }) => treatment || 'N/A'
    },
    {
      Header: 'Additional Metadata Fields',
      accessor: ({ additional_metadata: data }) => Object.keys(data).join(', ')
    }
  ]

  return (
    <Table
      columns={columns}
      data={samples}
      filter
      stickies={stickies}
      pageSize={5}
      pageSizeOptions={[5, 10, 20, 50]}
      selectedRows={selectedSamples}
      onFilteredRowsChange={setFilteredSamples}
    >
      <Box direction="row" justify="end" pad={{ bottom: 'medium' }}>
        <Button label="Add to Dataset" primary />
      </Box>
    </Table>
  )
}
