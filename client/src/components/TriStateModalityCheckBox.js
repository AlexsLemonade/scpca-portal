import React from 'react'
import { Box } from 'grommet'
import { FormCheckmark } from 'grommet-icons'
import { useMyDataset } from 'hooks/useMyDataset'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'

// NOTE: Ask Deepa for a checkmark SVG Icon
export const TriStateModalityCheckBox = ({
  project,
  modality,
  disabled,
  editable = false
}) => {
  const { getDatasetProjectData } = useMyDataset()
  const { filteredSamples, selectedSamples, toggleSamples } =
    useDatasetSamplesTable()

  const borderRegular = !isNoneSelected && !disabled ? 'brand' : 'black-tint-60'
  const borderColor = disabled ? 'black-tint-80' : borderRegular

  const sampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)
  const currentSelectedSamples = selectedSamples[modality]

  const selectedCountOnPage = sampleIdsOnPage.filter((id) =>
    currentSelectedSamples.includes(id)
  ).length

  const isNoneSelected = selectedCountOnPage === 0
  const isAllSelected = selectedCountOnPage === sampleIdsOnPage.length
  const isSomeSelected = !isNoneSelected && !isAllSelected

  const handleToggleAllSamples = () => {
    if (disabled || (!editable && isAllSelected)) return

    if (!editable) {
      // Exclude toggling samples in myDataset if the table is non-editable
      const samplesToExclude = getDatasetProjectData(project)[modality] || []
      toggleSamples(modality, samplesToExclude)
    } else {
      toggleSamples(modality)
    }
  }

  return (
    <Box
      align="center"
      border={{
        side: 'all',
        color: borderColor
      }}
      justify="center"
      round="4px"
      width="24px"
      height="24px"
      style={{ pointerEvents: disabled ? 'none' : 'auto' }}
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
