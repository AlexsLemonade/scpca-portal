import React from 'react'
import { Box, CheckBox } from 'grommet'
import { FormField } from 'components/FormField'

export const DatasetSamplesProjectOptions = ({
  project,
  includeBulk,
  onIncludeBulkChange
}) => {
  return (
    <FormField label="Project Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Include all bulk RNA-seq data in the project"
          checked={includeBulk}
          disabled={!project.has_bulk_rna_seq}
          onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
        />
      </Box>
    </FormField>
  )
}

export default DatasetSamplesProjectOptions
