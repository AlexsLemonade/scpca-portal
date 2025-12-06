import React from 'react'
import { CheckBoxGroup } from 'grommet'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  modalities,
  onModalitiesChange
}) => {
  const modalityOptions = getReadableOptions(getProjectModalities(project))

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={modalityOptions}
        value={modalities}
        onChange={({ value }) => onModalitiesChange(value)}
      />
    </FormField>
  )
}

export default DatasetProjectModalityOptions
