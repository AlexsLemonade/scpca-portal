import React from 'react'
import { Box, Text } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getReadable } from 'helpers/getReadable'
import { CheckBox } from 'components/CheckBox'

const TriStateCheckBox = ({ modality }) => {
  const { getHeaderState, toggleModalitySamples } = useProjectSamplesTable()
  const { checked, disabled, indeterminate } = getHeaderState(modality)

  return (
    <CheckBox
      checked={checked}
      disabled={disabled}
      indeterminate={indeterminate}
      onChange={() => toggleModalitySamples(modality)}
    />
  )
}

export const ProjectSamplesTableModalityHeader = () => {
  const { project } = useProjectSamplesTable()
  const availableModalities = getProjectModalities(project)
  const isSingleModality = availableModalities.length === 1

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
        {availableModalities.map((m) => (
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
