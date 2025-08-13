import { useContext } from 'react'
import { DatasetSamplesTableContext } from 'contexts/DatasetSamplesTableContext'
import { uniqueArray } from 'helpers/uniqueArray'

export const useDatasetSamplesTable = () => {
  const {
    allSamples,
    setAllSamples,
    selectedSamples,
    setSelectedSamples,
    filteredSamples,
    setFilteredSamples
  } = useContext(DatasetSamplesTableContext)

  const selectModalitySamplesByIds = (modality, sampleIds) => {
    const samplesToBeSelected = allSamples
      .filter((s) => sampleIds.includes(s.scpca_id))
      .map((s) => s.scpca_id)

    setSelectedSamples((prev) => {
      const modalitySamples = prev[modality] || []

      return {
        ...prev,
        [modality]: uniqueArray([...modalitySamples, ...samplesToBeSelected])
      }
    })
  }

  // Bulk-add/remove only samples visible on the currently selected page
  const toggleAllSamples = (modality) => {
    setSelectedSamples((prevSelectedSamples) => {
      const currentSelectedSamples = prevSelectedSamples[modality]

      const modalityFlags = {
        SINGLE_CELL: 'has_single_cell_data',
        SPATIAL: 'has_spatial_data'
      }
      const modalitySampleIds = filteredSamples
        .filter((s) => s[modalityFlags[modality]])
        .map((s) => s.scpca_id)

      const isAllOrSomeSelected = modalitySampleIds.some((id) =>
        currentSelectedSamples.includes(id)
      )

      if (isAllOrSomeSelected) {
        return {
          ...prevSelectedSamples,
          [modality]: currentSelectedSamples.filter(
            (id) => !modalitySampleIds.includes(id)
          )
        }
      }

      return {
        ...prevSelectedSamples,
        [modality]: uniqueArray([
          ...currentSelectedSamples,
          ...modalitySampleIds
        ])
      }
    })
  }

  const toggleSample = (modality, sample) => {
    setSelectedSamples((prevSelectedSamples) => {
      const currentSelectedSample = prevSelectedSamples[modality]
      const sampleId = sample.scpca_id

      const isSelected = currentSelectedSample.includes(sampleId)

      if (!isSelected) {
        return {
          ...prevSelectedSamples,
          [modality]: [...currentSelectedSample, sampleId]
        }
      }

      return {
        ...prevSelectedSamples,
        [modality]: currentSelectedSample.filter((id) => id !== sampleId)
      }
    })
  }

  return {
    allSamples,
    setAllSamples,
    selectedSamples,
    filteredSamples,
    setFilteredSamples,
    selectModalitySamplesByIds,
    toggleSample,
    toggleAllSamples
  }
}
