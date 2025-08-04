import React from 'react'
import { Box } from 'grommet'
import { FormCheckmark } from 'grommet-icons'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'

// NOTE: Ask Deepa for a checkmark SVG Icon
export const TriStateModalityCheckBox = ({ modality }) => {
  const { selectedSamples, filteredSamples, toggleAllSamples } =
    useDatasetSamplesTable()

  const sampleIdsOnPage = filteredSamples.map((sample) => sample.scpca_id)
  const currentSelectedSamples = selectedSamples[modality]

  const selectedCountOnPage = sampleIdsOnPage.filter((id) =>
    currentSelectedSamples.includes(id)
  ).length

  const isNoneSelected = selectedCountOnPage === 0
  const isAllSelected = selectedCountOnPage === sampleIdsOnPage.length
  const isSomeSelected = !isNoneSelected && !isAllSelected

  return (
    <Box
      align="center"
      border={{
        side: 'all',
        color: !isNoneSelected ? 'brand' : 'black-tint-60'
      }}
      justify="center"
      round="4px"
      width="24px"
      height="24px"
      onClick={() => toggleAllSamples(modality)}
    >
      {isSomeSelected && (
        <Box background="brand" round="inherit" width="10px" height="3px" />
      )}
      {isAllSelected && <FormCheckmark color="brand" size="20px" />}
    </Box>
  )
}

export default TriStateModalityCheckBox
