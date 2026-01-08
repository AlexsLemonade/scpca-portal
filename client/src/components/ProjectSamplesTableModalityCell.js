import React from 'react'
import { Box } from 'grommet'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { CheckBox } from 'components/CheckBox'

export const ProjectSamplesTableModalityCell = ({ sample }) => {
  const {
    project,
    getCheckBoxIsChecked,
    getCheckBoxIsDisabled,
    toggleSampleModality
  } = useProjectSamplesTable()

  const availableModalities = getProjectModalities(project)

  return (
    <Box align="center" direction="row" justify="around">
      {availableModalities.map((m) => (
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
