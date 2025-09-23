import React from 'react'
import { Select } from 'grommet'
import { config } from 'config'
import { useMyDataset } from 'hooks/useMyDataset'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetDataFormatOptions = ({
  project,
  format,
  onFormatChange
}) => {
  const { myDataset } = useMyDataset()

  const formatOptions = getReadableOptions(getProjectFormats(project))

  return (
    <FormField
      label={
        <HelpLink label="Data Format" link={config.links.what_downloading} />
      }
      labelWeight="bold"
      fieldWidth="200px"
    >
      <Select
        options={formatOptions}
        labelKey="label"
        disabled={!!myDataset.id}
        valueKey={{ key: 'value', reduce: true }}
        value={format || myDataset.format || formatOptions[0]}
        onChange={({ value }) => onFormatChange(value)}
      />
    </FormField>
  )
}

export default DatasetDataFormatOptions
