import { useContext } from 'react'
import { DatasetSamplesTableContext } from 'contexts/DatasetSamplesTableContext'
import { uniqueArray } from 'helpers/uniqueArray'

export const useDatasetSamplesTable = () => {
  const {
    selectedSamples,
    setSelectedSamples,
    filteredSamples,
    setFilteredSamples
  } = useContext(DatasetSamplesTableContext)

  // Bulk-add/remove only samples visible on the currently selected page
  const toggleAllSamples = (modality) => {
    setSelectedSamples((prevSelectedSamples) => {
      const currentSelectedSamples = prevSelectedSamples[modality]
      const sampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)

      const isAllOrSomeSelected = sampleIdsOnPage.some((id) =>
        currentSelectedSamples.includes(id)
      )

      if (isAllOrSomeSelected) {
        return {
          ...prevSelectedSamples,
          [modality]: currentSelectedSamples.filter(
            (id) => !sampleIdsOnPage.includes(id)
          )
        }
      }

      return {
        ...prevSelectedSamples,
        [modality]: uniqueArray([...currentSelectedSamples, ...sampleIdsOnPage])
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
    selectedSamples,
    filteredSamples,
    getFilteredSamples: setFilteredSamples,
    toggleSample,
    toggleAllSamples
  }
}
