import React from 'react'
import { Box } from 'grommet'
import { FormCheckmark } from 'grommet-icons'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'

export const TriStateModalityCheckBox = ({ project, modality }) => {
  const { getDatasetProjectData } = useMyDataset()
  const { canAdd, readOnly, filteredSamples, selectedSamples, toggleSamples } =
    useProjectSamplesTable()

  const sampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)
  const currentSelectedSamples = selectedSamples[modality]

  const selectedCountOnPage = sampleIdsOnPage.filter((id) =>
    currentSelectedSamples.includes(id)
  ).length

  const isNoneSelected = selectedCountOnPage === 0
  const isAllSelected = selectedCountOnPage === sampleIdsOnPage.length
  const isSomeSelected = !isNoneSelected && !isAllSelected

  const handleToggleAllSamples = () => {
    if (readOnly) return

    // Exclude toggling already added samples in the project samples table
    if (canAdd) {
      const samplesAlreadyAdded = getDatasetProjectData(project)[modality] || []
      toggleSamples(modality, samplesAlreadyAdded)
    } else {
      toggleSamples(modality)
    }
  }

  return (
    <Box
      align="center"
      border={{
        side: 'all',
        color: 'brand'
      }}
      justify="center"
      round="4px"
      width="24px"
      height="24px"
      onClick={handleToggleAllSamples}
    >
      {isSomeSelected && (
        <Box background="brand" round="inherit" width="10px" height="3px" />
      )}
      {isAllSelected && <FormCheckmark color="brand" size="20px" />}
    </Box>
  )
}

export default TriStateModalityCheckBox
