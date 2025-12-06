import React, { useEffect } from 'react'
import { Box, CheckBox } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { FormField } from 'components/FormField'

export const DatasetSamplesProjectOptions = ({
  project,
  includeBulk,
  onIncludeBulkChange
}) => {
  const { myDataset, isProjectIncludeBulk } = useMyDataset()

  // Preselect options based on the values in myDataset
  useEffect(() => {
    if (!myDataset) return

    onIncludeBulkChange(isProjectIncludeBulk(project))
  }, [myDataset])

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
