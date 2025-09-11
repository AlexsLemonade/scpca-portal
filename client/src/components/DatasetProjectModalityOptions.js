import React, { useEffect, useState } from 'react'
import { CheckBoxGroup } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { getReadable } from 'helpers/getReadable'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  modalities,
  onModalitiesChange
}) => {
  const { myDataset, datasetProjectOptions } = useMyDataset()

  const [isTouched, setIsTouched] = useState(false)

  const isAnnData = myDataset.format === 'ANN_DATA'
  const modalityOptions = [
    { key: 'SINGLE_CELL', value: project.has_single_cell_data },
    { key: 'SPATIAL', value: project.has_spatial_data }
  ]
    .filter((m) => m.value)
    .map(({ key }) => ({
      label: getReadable([key]),
      value: key,
      // Disable the SPATIAL checkbox for ANN_DATA
      disabled: key === 'SPATIAL' && isAnnData
    }))

  // Preselect modalities based on the most recently added project
  useEffect(() => {
    if (!isTouched) {
      const savedModalities = datasetProjectOptions.modalities

      if (savedModalities.length > 0) {
        const updatedModalities = savedModalities.filter((m) =>
          modalityOptions.some((mo) => mo.value === m)
        )
        onModalitiesChange(updatedModalities)
      }
      setIsTouched(true)
    }
  }, [isTouched, datasetProjectOptions, modalityOptions])

  // TODO: Remove this block once BE API is updated
  // Deselect and disable the SPATIAL checkbox if ANN_DATA is selected
  useEffect(() => {
    if (isAnnData && modalities.includes('SPATIAL')) {
      const updated = modalities.filter((m) => m !== 'SPATIAL')
      if (updated.length !== modalities.length) {
        onModalitiesChange(updated)
      }
    }
  }, [isAnnData, modalities])

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
