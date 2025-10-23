import { useContext } from 'react'
import { ProjectSamplesTableContext } from 'contexts/ProjectSamplesTableContext'
import { useMyDataset } from 'hooks/useMyDataset'
import { differenceArray } from 'helpers/differenceArray'
import { uniqueArray } from 'helpers/uniqueArray'

export const useProjectSamplesTable = () => {
  const {
    project,
    samples,
    canAdd,
    canRemove,
    readOnly,
    allSamples,
    setAllSamples,
    selectedSamples,
    setSelectedSamples,
    filteredSamples,
    setFilteredSamples
  } = useContext(ProjectSamplesTableContext)
  const {
    myDataset,
    userFormat,
    getDatasetProjectDataSamples,
    getProjectSingleCellSamples
  } = useMyDataset()

  const showBulkInfoText = canAdd && project && project.has_bulk_rna_seq

  const showWarningMultiplexed =
    canAdd &&
    project.has_multiplexed_data &&
    (myDataset.format || userFormat) === 'ANN_DATA'

  const getIsSampleInMyDataset = (sample, modality) => {
    const datasetProjectData = getDatasetProjectDataSamples(project, samples)
    return datasetProjectData[modality].includes(sample.scpca_id)
  }

  const getHasModality = (sample, modality) =>
    sample[`has_${modality.toLowerCase()}_data`]

  const getCheckBoxIsChecked = (sample, modality) =>
    selectedSamples[modality].includes(sample.scpca_id)

  const getCheckBoxIsDisabled = (sample, modality) => {
    if (canAdd) {
      return (
        !getHasModality(sample, modality) ||
        getIsSampleInMyDataset(sample, modality)
      )
    }

    if (canRemove) {
      return !getHasModality(sample, modality)
    }

    return true
  }

  // Get the current state of the tri-state checkbox
  const getTriState = (modality) => {
    const allSampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)
    const selectedModalitySampleIds = selectedSamples[modality]

    const selectedSampleIdsOnPage = allSampleIdsOnPage.filter((id) =>
      selectedModalitySampleIds.includes(id)
    )

    const isNoneSelected = selectedSampleIdsOnPage.length === 0
    const isAllSelected =
      selectedSampleIdsOnPage.length === allSampleIdsOnPage.length
    const isSomeSelected = !isNoneSelected && !isAllSelected

    return {
      checked: isAllSelected,
      disabled: readOnly,
      indeterminate: isSomeSelected
    }
  }

  const selectAllSingleCellSamples = () => {
    setSelectedSamples((prevSelectedSamples) => ({
      ...prevSelectedSamples,
      SINGLE_CELL: getProjectSingleCellSamples(project.samples)
    }))
  }

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

  // Add or remove samples visible on the currently selected page
  const toggleSamples = (modality) => {
    if (readOnly) return

    setSelectedSamples((prevSelectedSamples) => {
      const currentSelectedSamples = prevSelectedSamples[modality]

      const modalitySampleIds = filteredSamples
        .filter((s) => s[`has_${modality.toLowerCase()}_data`])
        .map((s) => s.scpca_id)

      // Exclude toggling of already-added samples on the Browse page
      const alreadyAddedSampleIds = canAdd
        ? getDatasetProjectDataSamples(project, samples)[modality] || []
        : []

      const sampleIdsToToggle = differenceArray(
        modalitySampleIds,
        alreadyAddedSampleIds
      )

      const isAllOrSomeSelected = sampleIdsToToggle.some((id) =>
        currentSelectedSamples.includes(id)
      )

      if (isAllOrSomeSelected) {
        return {
          ...prevSelectedSamples,
          [modality]: currentSelectedSamples.filter(
            (id) => !sampleIdsToToggle.includes(id)
          )
        }
      }

      return {
        ...prevSelectedSamples,
        [modality]: uniqueArray([
          ...currentSelectedSamples,
          ...sampleIdsToToggle
        ])
      }
    })
  }

  // Add or remove a sample visible on the currently selected page
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
    project,
    samples,
    canAdd,
    canRemove,
    readOnly,
    allSamples,
    setAllSamples,
    selectedSamples,
    filteredSamples,
    setFilteredSamples,
    showBulkInfoText,
    showWarningMultiplexed,
    getTriState,
    getCheckBoxIsChecked,
    getCheckBoxIsDisabled,
    selectAllSingleCellSamples,
    selectModalitySamplesByIds,
    toggleSample,
    toggleSamples
  }
}
