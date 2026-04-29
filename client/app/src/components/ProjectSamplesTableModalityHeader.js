import React from 'react'
import { Box, Text } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getReadable } from 'helpers/getReadable'
import { CheckBox } from 'components/CheckBox'

export const ProjectSamplesTableModalityHeader = () => {
  const {
    project,
    readOnly,
    getIsAllSelected,
    getIsSomeSelected,
    toggleModalitySamples
  } = useProjectSamplesTable()
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
            <CheckBox
              checked={getIsAllSelected(m)}
              disabled={readOnly}
              indeterminate={getIsSomeSelected(m)}
              onChange={() => toggleModalitySamples(m)}
            />
          </Box>
        ))}
      </Box>
    </>
  )
}
