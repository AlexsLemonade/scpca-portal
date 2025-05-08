import React, { useState } from 'react'
import { Select } from 'grommet'
import { config } from 'config'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetProjectDataFormat = () => {
  // NOTE: The dataset endpoint should include all available format options fields per resource
  const formatOptions = ['SINGLE_CELL_EXPERIMENT', 'ANN_DATA']
  const [format, setFormat] = useState(formatOptions[0])

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
        valueKey={{ key: 'value', reduce: true }}
        value={format || formatOptions[0]}
        onChange={({ value }) => setFormat(value)}
      />
    </FormField>
  )
}

export default DatasetProjectDataFormat
