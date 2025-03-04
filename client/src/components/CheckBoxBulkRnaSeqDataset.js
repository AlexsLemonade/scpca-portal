import React from 'react'
import { Box, CheckBox } from 'grommet'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'

export const CheckBoxBulkRnaSeqDataset = () => {
  const { includeBulkRnaSeq, setIncludeBulkRnaSeq, isBulkRnaSeqAvailable } =
    useDatasetOptionsContext()

  const handleChange = () => {
    setIncludeBulkRnaSeq(!includeBulkRnaSeq)
  }

  if (!isBulkRnaSeqAvailable) return null

  return (
    <>
      <Box direction="row">
        <CheckBox
          label="Include all bulk RNA-seq data in the project"
          onChange={handleChange}
        />
      </Box>
    </>
  )
}

export default CheckBoxBulkRnaSeqDataset
