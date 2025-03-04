import React from 'react'
import { CheckBoxGroup } from 'grommet'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'

export const CheckBoxGroupModalityDataset = () => {
  const { modalityOptions, setSelectedModalities } = useDatasetOptionsContext()

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={getReadableOptions(modalityOptions)}
        onChange={(event) => setSelectedModalities(event.value)}
      />
    </FormField>
  )
}

export default CheckBoxGroupModalityDataset
