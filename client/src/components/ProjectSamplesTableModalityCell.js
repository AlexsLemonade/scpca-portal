import React from 'react'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { CheckBox } from 'components/CheckBox'

export const ProjectSamplesTableModalityCell = ({ modality, sample }) => {
  const { getCheckBoxIsChecked, getCheckBoxIsDisabled, toggleSample } =
    useProjectSamplesTable()

  const handleToggleSample = () => toggleSample(modality, sample)

  return (
    <CheckBox
      name={modality}
      checked={getCheckBoxIsChecked(sample, modality)}
      disabled={getCheckBoxIsDisabled(sample, modality)}
      onClick={handleToggleSample}
    />
  )
}

export default ProjectSamplesTableModalityCell
