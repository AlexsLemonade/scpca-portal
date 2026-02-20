import React, { useState } from 'react'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'

import { Button } from 'components/Button'

export const DatasetSaveAndGoBackButton = ({
  project,
  includeBulk,
  includeMerge
}) => {
  const { asPath, back } = useRouter()
  const { setRestoreFromDestination } = useScrollRestore()
  const { setMyDatasetSamples } = useMyDataset()
  const { selectedSamples } = useProjectSamplesTable()

  const [saving, setSaving] = useState(false)
  const handleSaveAndGoBack = async () => {
    setSaving(true)
    const newSamplesToAdd = {
      ...selectedSamples,
      ...(includeMerge && { SINGLE_CELL: 'MERGED' })
    }

    const datasetRequest = await setMyDatasetSamples(project, {
      ...newSamplesToAdd,
      includes_bulk: includeBulk
    })

    if (datasetRequest) {
      setRestoreFromDestination(asPath)
      back()
    } else {
      // TODO: Error handling
    }
    setSaving(false)
  }

  return (
    <Button
      primary
      label="Save & Go Back"
      loading={saving}
      onClick={handleSaveAndGoBack}
    />
  )
}

export default DatasetSaveAndGoBackButton
