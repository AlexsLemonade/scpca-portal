import React from 'react'
import { Box, Text } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { CheckBox } from 'components/CheckBox'

const TriStateCheckBox = ({ modality }) => {
  const { readOnly, getHeaderState, toggleModalitySamples } =
    useProjectSamplesTable()
  const { checked, disabled, indeterminate } = getHeaderState(modality)

  const handleToggleAllSamples = () => {
    if (readOnly) return
    toggleModalitySamples(modality)
  }

  return (
    <CheckBox
      checked={checked}
      disabled={disabled}
      indeterminate={indeterminate}
      onChange={handleToggleAllSamples}
    />
  )
}

export const ProjectSamplesTableModalityHeader = ({ modalities }) => {
  const isSingleModality = modalities.length === 1
  const checkBoxCellWidth = isSingleModality ? '50px' : '200px'

  return (
    <Box width={checkBoxCellWidth}>
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
    </Box>
  )
}
