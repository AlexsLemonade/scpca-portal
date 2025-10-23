import React from 'react'
import { Box, Text } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { CheckBox } from 'components/CheckBox'

const TriStateCheckBox = ({ modality }) => {
  const { readOnly, getTriState, toggleSamples } = useProjectSamplesTable()
  const { isAllSelected, isSomeSelected } = getTriState(modality)

  const handleToggleAllSamples = () => {
    if (readOnly) return
    toggleSamples(modality)
  }

  return (
    <CheckBox
      checked={isAllSelected}
      indeterminate={isSomeSelected}
      disabled={readOnly}
      onChange={handleToggleAllSamples}
    />
  )
}

export const ProjectSamplesTableModalityHeaderCell = ({ modalities }) => {
  const isSingleModality = modalities.length === 1

  return (
    <>
      {!isSingleModality && (
        <>
          <Box align="center" margin={{ bottom: 'small' }} pad="small">
            Select Modality
          </Box>
          <Box
            border={{ side: 'bottom' }}
            width="100%"
            style={{ position: 'absolute', top: '45px', left: 0 }}
          />
        </>
      )}
      <Box direction="row" justify="around">
        {modalities.map((m) => (
          <Box
            key={m}
            align="center"
            margin={
              isSingleModality ? { left: 'medium', vertical: 'medium' } : '0'
            }
            pad={!isSingleModality ? { horizontal: 'small' } : '0'}
          >
            {!isSingleModality && (
              <Text margin={{ bottom: 'xsmall' }}>{getReadable(m)}</Text>
            )}
            <TriStateCheckBox modality={m} />
          </Box>
        ))}
      </Box>
    </>
  )
}
