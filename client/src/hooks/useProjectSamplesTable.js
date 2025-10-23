import { useContext, useEffect } from 'react'
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
    getDatasetProjectData,
    getProjectSingleCellSamples
  } = useMyDataset()

  // Preselect samples in the table that are already added in myDataset
  useEffect(() => {
    const { SINGLE_CELL: singleCellSamples, SPATIAL: spatialSamples } =
      getDatasetProjectData(project)

    if (singleCellSamples) {
      // Select all SINGLE_CELL samples if the project is merged
      const samplesToSelect =
        singleCellSamples === 'MERGED'
          ? allSamples
              .filter((s) => s.has_single_cell_data)
              .map((s) => s.scpca_id)
          : singleCellSamples

      selectModalitySamplesByIds('SINGLE_CELL', samplesToSelect)
    }

    if (spatialSamples) {
      selectModalitySamplesByIds('SPATIAL', spatialSamples)
    }
  }, [myDataset, allSamples])

  const showBulkInfoText = canAdd && project && project.has_bulk_rna_seq

  const showWarningMultiplexed =
    canAdd &&
    project.has_multiplexed_data &&
    (myDataset.format || userFormat) === 'ANN_DATA'

  const getIsSampleInMyDataset = (sample, modality) => {
    const datasetData = getDatasetProjectData(project)

    const datasetModalitiesSamples = {
      SINGLE_CELL:
        datasetData.SINGLE_CELL === 'MERGED'
          ? getProjectSingleCellSamples(samples)
          : datasetData.SINGLE_CELL || [],
      SPATIAL: datasetData.SPATIAL || []
    }

    return datasetModalitiesSamples[modality].includes(sample.scpca_id)
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
      isAllSelected,
      isSomeSelected
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
        ? getDatasetProjectData(project)[modality] || []
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
    toggleSample,
    toggleSamples
  }
}
