import React from 'react'
import { Box } from 'grommet'
import { FormCheckmark } from 'grommet-icons'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'

// NOTE: Ask Deepa for a checkmark SVG Icon
export const TriStateModalityCheckBox = ({ modality, disabled }) => {
  const { myDataset } = useDatasetManager()
  const { filteredSamples, selectedSamples, toggleAllSamples } =
    useDatasetSamplesTable()

  const disableSpatial =
    modality === 'SPATIAL' && myDataset?.format === 'ANN_DATA'

  const borderRegular = !isNoneSelected && !disabled ? 'brand' : 'black-tint-60'
  const borderColor =
    disabled || disableSpatial ? 'black-tint-80' : borderRegular

  const sampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)
  const currentSelectedSamples = selectedSamples[modality]

  const selectedCountOnPage = sampleIdsOnPage.filter((id) =>
    currentSelectedSamples.includes(id)
  ).length

  const isNoneSelected = selectedCountOnPage === 0
  const isAllSelected = selectedCountOnPage === sampleIdsOnPage.length
  const isSomeSelected = !isNoneSelected && !isAllSelected

  const handleToggleAllSamples = () => {
    if (disabled) return
    toggleAllSamples(modality)
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
      style={{ pointerEvents: disabled || disableSpatial ? 'none' : 'auto' }}
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
