import React from 'react'
import { Box } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { CheckBox } from 'components/CheckBox'

export const ProjectSamplesTableModalityCell = ({ sample, modalities }) => {
  const { getCheckBoxIsChecked, getCheckBoxIsDisabled, toggleSampleModality } =
    useProjectSamplesTable()

  const checkBoxCellWidth = modalities.length > 1 ? '200px' : '50px'

  return (
    <Box
      align="center"
      direction="row"
      justify="around"
      width={checkBoxCellWidth}
    >
      {modalities.map((m) => (
        <CheckBox
          key={`${sample.scpca_id}_${m}`}
          name={m}
          checked={getCheckBoxIsChecked(sample, m)}
          disabled={getCheckBoxIsDisabled(sample, m)}
          onClick={() => toggleSampleModality(sample, m)}
        />
      ))}
    </Box>
  )
}

export default ProjectSamplesTableModalityCell
