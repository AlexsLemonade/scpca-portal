import React, { useEffect } from 'react'
import { Box, CheckBox } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { FormField } from 'components/FormField'

export const DatasetSamplesProjectOptions = ({
  project,
  includeBulk,
  onIncludeBulkChange
}) => {
  const { myDataset } = useDatasetManager()

  useEffect(() => {
    const projectData = myDataset?.data?.[project.scpca_id]
    if (projectData) {
      onIncludeBulkChange(projectData.includes_bulk)
    }
  }, [myDataset])

  return (
    <FormField label="Project Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Include all bulk RNA-seq data in the project"
          checked={includeBulk}
          onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
        />
      </Box>
    </FormField>
  )
}

export default DatasetSamplesProjectOptions
