import React from 'react'
import { Box, Text } from 'grommet'
import { getReadable } from 'helpers/getReadable'
import { TriStateModalityCheckBox } from 'components/TriStateModalityCheckBox'

const SingleModalityCheckBox = ({ project, modalities, editable }) => {
  return (
    <>
      {modalities.map((m) => (
        <Box
          key={m}
          align="center"
          margin={{ left: 'medium', vertical: 'medium' }}
        >
          <TriStateModalityCheckBox
            project={project}
            modality={m}
            disabled={!project[`has_${m.toLowerCase()}_data`]}
            editable={editable}
          />
        </Box>
      ))}
    </>
  )
}

export const TriStateModalityCheckBoxHeader = ({
  project,
  modalities,
  editable
}) => {
  const isSingleModality = modalities.length === 1

  return (
    <>
      {isSingleModality ? (
        <SingleModalityCheckBox
          project={project}
          modalities={modalities}
          editable={editable}
        />
      ) : (
        <>
          <Box align="center" margin={{ bottom: 'small' }} pad="small">
            Select Modality
          </Box>
          <Box
            border={{ side: 'bottom' }}
            width="100%"
            style={{ position: 'absolute', top: '45px', left: 0 }}
          />
          <Box direction="row" justify="around">
            {modalities.map((m) => (
              <Box key={m} align="center" pad={{ horizontal: 'small' }}>
                <Text margin={{ bottom: 'xsmall' }}>{getReadable(m)}</Text>
                <TriStateModalityCheckBox
                  project={project}
                  modality={m}
                  disabled={!project[`has_${m.toLowerCase()}_data`]}
                  editable={editable}
                />
              </Box>
            ))}
          </Box>
        </>
      )}
    </>
  )
}
