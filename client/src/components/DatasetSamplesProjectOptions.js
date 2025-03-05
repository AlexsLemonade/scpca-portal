import React from 'react'
import { Box, CheckBox } from 'grommet'
import { FormField } from 'components/FormField'

export const DatasetSampesProjectOptions = () => {
  const handleChange = () => {}

  return (
    <FormField label="Project Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Include all bulk RNA-seq data in the project"
          onChange={handleChange}
        />
      </Box>
    </FormField>
  )
}

export default DatasetSampesProjectOptions
