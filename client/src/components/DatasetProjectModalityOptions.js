import React, { useEffect } from 'react'
import { CheckBoxGroup } from 'grommet'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  format, // TODO: Remove this once Spatial && ANN_DATA allowed
  modalities,
  onModalitiesChange
}) => {
  // TODO: Remove this once Spatial && ANN_DATA allowed
  const modalityOptions = getReadableOptions(getProjectModalities(project)).map(
    (mo) =>
      mo.value === 'SPATIAL' && format === 'ANN_DATA'
        ? {
            ...mo,
            disabled: true
          }
        : mo
  )

  // TODO: Remove this once Spatial && ANN_DATA allowed
  // Deselect and disable the SPATIAL checkbox if ANN_DATA is selected
  useEffect(() => {
    if (format === 'ANN_DATA' && modalities.includes('SPATIAL')) {
      onModalitiesChange(modalities.filter((m) => m !== 'SPATIAL'))
    }
  }, [modalities, format])

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
