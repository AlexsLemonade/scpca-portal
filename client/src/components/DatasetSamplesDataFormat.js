import React from 'react'
import { Box, Select } from 'grommet'
import { config } from 'config'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetSamplesDataFormat = ({
  project,
  availableFormats,
  format,
  onFormatChange
}) => {
  const { myDataset } = useDatasetManager()
  const { hasSelectedSpatialSamples } = useDatasetSamplesTable()

  const selectOptions = availableFormats.map((f) => ({
    label: getReadable(f),
    value: f,
    // Disable the ANN_DATA option when it's not available,
    // or spatial samples are added
    disabled:
      (f === 'ANN_DATA' && hasSelectedSpatialSamples()) ||
      !project.includes_anndata
  }))

  const handleFormatChange = (value) => {
    const selectedOption = selectOptions.find((opt) => opt.value === value)
    if (selectedOption?.disabled) return
    onFormatChange(value)
  }

  return (
    <FormField
      label={
        <HelpLink label="Data Format" link={config.links.what_downloading} />
      }
      labelWeight="bold"
      fieldWidth="200px"
    >
      <Select
        options={selectOptions}
        labelKey="label"
        valueKey={{ key: 'value', reduce: true }}
        value={format}
        disabled={!!myDataset.format}
        // eslint-disable-next-line react/no-children-prop
        children={(option, index, options, { active }) => {
          const isDisabled = option.disabled
          const backgroundActiveDefault =
            active && !isDisabled ? 'brand' : undefined
          const backgroundActiveDisabled = active ? 'black-tint-95' : undefined
          return (
            <Box
              pad={{ vertical: 'small', horizontal: 'medium' }}
              background={backgroundActiveDefault || backgroundActiveDisabled}
              style={{
                cursor: isDisabled ? 'not-allowed' : 'pointer'
              }}
            >
              {option.label}
            </Box>
          )
        }}
        onChange={({ value }) => handleFormatChange(value)}
      />
    </FormField>
  )
}

export default DatasetSamplesDataFormat
