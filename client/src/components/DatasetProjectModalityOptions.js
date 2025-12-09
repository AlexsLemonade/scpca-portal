import React, { useEffect, useState } from 'react'
import { CheckBoxGroup } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { uniqueArray } from 'helpers/uniqueArray'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  modalities,
  onModalitiesChange
}) => {
  const { myDataset, getDatasetProjectData } = useMyDataset()
  const modalityOptions = getReadableOptions(getProjectModalities(project))
  const [options, setOptions] = useState([])
  const [addedModalities, setAddedModalities] = useState([])

  useEffect(() => {
    const projectData = getDatasetProjectData(project)
    // Check if any modality sample has been added to myDataset
    const modalityStates = Object.keys(projectData).filter((key) => {
      const v = projectData[key]
      return (Array.isArray(v) && v.length > 0) || v === 'MERGED'
    })
    // Preselect and disable the modality checkbox if it has been added
    // to restrict the user from removing added samples
    const mergedOptions = modalityOptions.map((mo) => ({
      ...mo,
      disabled: modalityStates.includes(mo.value)
    }))

    setAddedModalities(modalityStates)
    setOptions(mergedOptions)
  }, [myDataset, project])

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={options}
        value={uniqueArray(modalities, addedModalities)}
        onChange={({ value }) => onModalitiesChange(value)}
      />
    </FormField>
  )
}

export default DatasetProjectModalityOptions
