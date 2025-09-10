import React, { useEffect } from 'react'
import { Select } from 'grommet'
import { config } from 'config'
import { useMyDataset } from 'hooks/useMyDataset'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetDataFormatOptions = ({ project }) => {
  const { myDataset, setMyDataset, userFormat } = useMyDataset()

  const formatOptions = [
    { key: 'SINGLE_CELL_EXPERIMENT', value: project.has_single_cell_data },
    { key: 'ANN_DATA', value: project.includes_anndata }
  ]
    .filter((f) => f.value)
    .map((f) => f.key)

  const defaultFormat = formatOptions.includes(userFormat)
    ? userFormat
    : formatOptions[0]

  const handleFormatChange = (value) => {
    setMyDataset((prev) => ({ ...prev, format: value }))
  }

  useEffect(() => {
    if (!myDataset.format) {
      setMyDataset((prev) => ({ ...prev, format: defaultFormat }))
    }
  }, [myDataset])

  return (
    <FormField
      label={
        <HelpLink label="Data Format" link={config.links.what_downloading} />
      }
      labelWeight="bold"
      fieldWidth="200px"
    >
      <Select
        options={getReadableOptions(formatOptions)}
        labelKey="label"
        disabled={!!myDataset.id}
        valueKey={{ key: 'value', reduce: true }}
        value={myDataset.format}
        onChange={({ value }) => handleFormatChange(value)}
      />
    </FormField>
  )
}

export default DatasetDataFormatOptions
