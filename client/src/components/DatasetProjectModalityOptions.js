import React from 'react'
import { CheckBoxGroup } from 'grommet'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({ project }) => {
  const handleChange = () => {}
  // NOTE: All available modality options per project will be populated via a hook
  const modalityOptions = [
    {
      key: 'SINGLE_CELL',
      value: project.has_single_cell_data
    },
    {
      key: 'SPATIAL',
      value: project.has_spatial_data
    }
  ]
    .filter((m) => m.value)
    .map((m) => m.key)

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={getReadableOptions(modalityOptions)}
        onChange={(event) => handleChange(event.value)}
      />
    </FormField>
  )
}

export default DatasetProjectModalityOptions
