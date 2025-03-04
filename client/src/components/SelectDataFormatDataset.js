import React from 'react'
import { Select } from 'grommet'
import { config } from 'config'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const SelectDataFormatDataset = () => {
  const { format, setFormat, formatOptions } = useDatasetOptionsContext()

  return (
    <FormField
      label={
        <HelpLink label="Data Format" link={config.links.what_downloading} />
      }
      labelWeight="bold"
      selectWidth="200px"
    >
      <Select
        options={getReadableOptions(formatOptions)}
        labelKey="label"
        valueKey={{ key: 'value', reduce: true }}
        value={format || formatOptions[0]}
        onChange={({ value }) => setFormat(value)}
      />
    </FormField>
  )
}

export default SelectDataFormatDataset
