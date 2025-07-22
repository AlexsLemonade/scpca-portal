import React, { useEffect } from 'react'
import { CheckBoxGroup } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { getReadable } from 'helpers/getReadable'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  format,
  modalities,
  handleSetModalities
}) => {
  const { myDataset } = useDatasetManager()

  const isAnnData = myDataset.format === 'ANN_DATA' || format === 'ANN_DATA'
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

  // Deselect and disable the SPATIAL checkbox if ANN_DATA is selected
  useEffect(() => {
    if (isAnnData && modalities.includes('SPATIAL')) {
      const updated = modalities.filter((m) => m !== 'SPATIAL')
      if (updated.length !== modalities.length) {
        handleSetModalities(updated)
      }
    }
  }, [isAnnData, modalities])

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={modalityOptions}
        value={modalities}
        onChange={({ value }) => handleSetModalities(value)}
      />
    </FormField>
  )
}

export default DatasetProjectModalityOptions
