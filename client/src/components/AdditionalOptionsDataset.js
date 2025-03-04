import React from 'react'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { CheckBoxBulkRnaSeqDataset } from 'components/CheckBoxBulkRnaSeqDataset'
import { CheckBoxExcludeMultiplexedDataset } from 'components/CheckBoxExcludeMultiplexedDataset'
import { CheckBoxMergedObjectsDataset } from 'components/CheckBoxMergedObjectsDataset'
import { FormField } from 'components/FormField'

export const AdditionalOptionsDataset = () => {
  const { resource } = useDatasetOptionsContext()
  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed
  } = resource

  return (
    <FormField label="Additional Options" gap="medium" labelWeight="bold">
      <CheckBoxMergedObjectsDataset
        label="Merge single-cell samples into 1 object"
        infoText="Merged objects are not available for projects with multiplexed samples."
      />
      {hasBulkRnaSeq && <CheckBoxBulkRnaSeqDataset />}
      {hasMultiplexed && <CheckBoxExcludeMultiplexedDataset />}
    </FormField>
  )
}

export default AdditionalOptionsDataset
