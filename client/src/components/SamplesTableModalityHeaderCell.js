import React from 'react'
import { Box, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { getReadable } from 'helpers/getReadable'
import { CheckBox } from 'components/CheckBox'

const TriStateCheckBox = ({ project, modality }) => {
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
    <CheckBox
      checked={isAllSelected}
      indeterminate={isSomeSelected}
      disabled={readOnly}
      onChange={handleToggleAllSamples}
    />
  )
}

export const SamplesTableModalityHeaderCell = ({ project, modalities }) => {
  const isSingleModality = modalities.length === 1

  return (
    <>
      {!isSingleModality && (
        <>
          <Box align="center" margin={{ bottom: 'small' }} pad="small">
            Select Modality
          </Box>
          <Box
            border={{ side: 'bottom' }}
            width="100%"
            style={{ position: 'absolute', top: '45px', left: 0 }}
          />
        </>
      )}
      <Box direction="row" justify="around">
        {modalities.map((m) => (
          <Box
            key={m}
            align="center"
            margin={
              isSingleModality ? { left: 'medium', vertical: 'medium' } : '0'
            }
            pad={!isSingleModality ? { horizontal: 'small' } : '0'}
          >
            {!isSingleModality && (
              <Text margin={{ bottom: 'xsmall' }}>{getReadable(m)}</Text>
            )}
            <TriStateCheckBox
              project={project}
              modality={m}
              disabled={!project[`has_${m.toLowerCase()}_data`]}
            />
          </Box>
        ))}
      </Box>
    </>
  )
}
