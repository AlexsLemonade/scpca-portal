import React from 'react'
import { Box, CheckBox as GrommetCheckBox, Text } from 'grommet'
import { FormCheckmark } from 'grommet-icons'
import styled, { css } from 'styled-components'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { Button } from 'components/Button'
import { Pill } from 'components/Pill'
import { Table } from 'components/Table'
import { getReadable } from 'helpers/getReadable'
import { getReadableModalities } from 'helpers/getReadableModalities'

const CheckBox = styled(GrommetCheckBox)`
  + div {
    width: 24px;
    height: 24px;
  }
  ${({ theme }) => css`
    &:not(:checked) {
      + div {
        background: ${theme.global.colors.white};
      }
    }
  `}
`

// NOTE: Ask Deepa for a checkmark SVG Icon
const TriStateModalityCheckBox = ({ modality }) => {
  const { selectedSamples, filteredSamples, toggleAllSamples } =
    useDatasetSamplesTable()

  const sampleIdsOnPage = filteredSamples.map((sample) => sample.scpca_id)
  const currentSelectedSamples = selectedSamples[modality]

  const selectedCountOnPage = sampleIdsOnPage.filter((id) =>
    currentSelectedSamples.includes(id)
  ).length

  const isNoneSelected = selectedCountOnPage === 0
  const isAllSelected = selectedCountOnPage === sampleIdsOnPage.length
  const isSomeSelected = !isNoneSelected && !isAllSelected

  return (
    <Box
      align="center"
      border={{
        side: 'all',
        color: !isNoneSelected ? 'brand' : 'black-tint-60'
      }}
      justify="center"
      round="4px"
      width="24px"
      height="24px"
      onClick={() => toggleAllSamples(modality)}
    >
      {isSomeSelected && (
        <Box background="brand" round="inherit" width="10px" height="3px" />
      )}
      {isAllSelected && <FormCheckmark color="brand" size="20px" />}
    </Box>
  )
}

const ModalityCheckBox = ({ modality, sampleId, disabled, onClick }) => {
  const { selectedSamples } = useDatasetSamplesTable()

  return (
    <CheckBox
      name={modality}
      checked={!disabled ? selectedSamples[modality].includes(sampleId) : false}
      disabled={disabled}
      onClick={onClick}
    />
  )
}

// NOTE: This component accepts 'samples' prop but it's subject to change
// Currently mock data is used via Storybook for development
// Some cells are removed teemporarily (e.g., multiplexed only cells)
export const DatasetSamplesTable = ({ samples, stickies = 3 }) => {
  const { selectedSamples, toggleSample, getFilteredSamples } =
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
    { Header: 'Sequencing Units', accessor: 'seq_units' },
    {
      Header: 'Modalities',
      accessor: ({ modalities }) =>
        [...getReadableModalities(modalities, true)].join(', ')
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
      onFilteredRowsChange={getFilteredSamples}
    >
      <Box direction="row" justify="end" pad={{ bottom: 'medium' }}>
        <Button label="Add to Dataset" primary />
      </Box>
    </Table>
  )
}
