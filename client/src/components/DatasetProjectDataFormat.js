import React, { useEffect, useState } from 'react'
import { Select } from 'grommet'
import { config } from 'config'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetProjectDataFormat = ({ project }) => {
  const { myDataset, userFormat, setUserFormat } = useDatasetManager()
  const [format, setFormat] = useState(myDataset.format || userFormat)

  const defaultOptions = [
    { key: 'SINGLE_CELL_EXPERIMENT', value: project.has_single_cell_data },
    { key: 'ANN_DATA', value: project.includes_anndata }
  ]
    .filter((f) => f.value)
    .map((f) => f.key)

  const handleFormatChange = (value) => {
    setFormat(value)
    setUserFormat(value)
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
        disabled={!!myDataset.format}
        options={getReadableOptions(defaultOptions)}
        labelKey="label"
        valueKey={{ key: 'value', reduce: true }}
        value={myDataset.format || format}
        onChange={({ value }) => handleSetFormat(value)}
      />
    </FormField>
  )
}

export default DatasetProjectDataFormat
