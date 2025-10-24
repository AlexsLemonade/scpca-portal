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
  const { myDataset, isDatasetDataEmpty } = useMyDataset()

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
        disabled={!!myDataset.id && !isDatasetDataEmpty}
        valueKey={{ key: 'value', reduce: true }}
        value={format}
        onChange={({ value }) => onFormatChange(value)}
      />
    </FormField>
  )
}

export default DatasetDataFormatOptions
