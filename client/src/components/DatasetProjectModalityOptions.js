import React, { useEffect, useState } from 'react'
import { CheckBoxGroup } from 'grommet'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { FormField } from 'components/FormField'

export const DatasetProjectModalityOptions = ({
  project,
  remainingSamples = {},
  modalities,
  onModalitiesChange
}) => {
  const [options, setOptions] = useState(
    getReadableOptions(getProjectModalities(project))
  )

  // Run only for the add remaining modal
  useEffect(() => {
    if (!remainingSamples || Object.keys(remainingSamples).length === 0) return

    // Filter for any remaining samples of each modality
    const remainingModalities = Object.keys(remainingSamples).filter(
      (m) => remainingSamples[m].length > 0
    )

    // Preselect and disable modalities if no samples remain
    setOptions((prev) =>
      prev.map((mo) => ({
        ...mo,
        disabled: !remainingModalities.includes(mo.value)
      }))
    )
  }, [remainingSamples])

  return (
    <FormField label="Modality" labelWeight="bold">
      <CheckBoxGroup
        options={options}
        value={modalities}
        onChange={({ value }) => onModalitiesChange(value)}
      />
    </FormField>
  )
}

export default DatasetProjectModalityOptions
