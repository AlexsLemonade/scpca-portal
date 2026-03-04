import React, { useEffect } from 'react'
import { Box, CheckBox } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { FormField } from 'components/FormField'

export const DatasetSamplesProjectOptions = ({
  project,
  includeBulk,
  onIncludeBulkChange
}) => {
  const { myDataset, isMyDatasetProjectIncludeBulk } = useMyDataset()

  // Preselect options based on the values in myDataset
  useEffect(() => {
    if (!myDataset) return

    onIncludeBulkChange(isMyDatasetProjectIncludeBulk(project))
  }, [myDataset])

  return (
    <FormField label="Project Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Include all bulk RNA-seq data in the project"
          checked={includeBulk}
          disabled={
            !project.has_bulk_rna_seq ||
            !!myDataset.data?.[project.scpca_id]?.includes_bulk
          }
          onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
        />
      </Box>
    </FormField>
  )
}

export default DatasetSamplesProjectOptions
