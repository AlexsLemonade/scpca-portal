import { useContext, useEffect } from 'react'
import { ProjectSamplesTableContext } from 'contexts/ProjectSamplesTableContext'
import { useMyDataset } from 'hooks/useMyDataset'
import { differenceArray } from 'helpers/differenceArray'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { uniqueArray } from 'helpers/uniqueArray'

export const useProjectSamplesTable = () => {
  const {
    project,
    samples,
    dataset,
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
    setUserFormat,
    getMyDatasetProjectDataSamples
  } = useMyDataset()

  // Set default userFormat value
  useEffect(() => {
    setUserFormat(myDataset.format || getProjectFormats(project)[0])
  }, [myDataset.format])

  const showBulkInfoText = canAdd && project.has_bulk_rna_seq

  const canAddMultiplexed = userFormat === 'SINGLE_CELL_EXPERIMENT'
  const showWarningMultiplexed =
    canAdd &&
    project.has_multiplexed_data &&
    (myDataset.format || userFormat) === 'ANN_DATA'

  const getIsSampleInMyDataset = (sample, modality) => {
    const datasetProjectData = getMyDatasetProjectDataSamples(project)
    return datasetProjectData[modality].includes(sample.scpca_id)
  }

  const getHasModality = (sample, modality) =>
    sample[`has_${modality.toLowerCase()}_data`]

  const getMultiplexedDisabled = (sample) =>
    // Multiplexed samples are not available for ANN_DATA
    myDataset.format === 'ANN_DATA' && sample.has_multiplexed_data

  const getCheckBoxIsChecked = (sample, modality) =>
    selectedSamples[modality].includes(sample.scpca_id)

  const getCheckBoxIsDisabled = (sample, modality) => {
    if (canAdd) {
      return (
        !getHasModality(sample, modality) ||
        getMultiplexedDisabled(sample) ||
        getIsSampleInMyDataset(sample, modality)
      )
    }

    if (canRemove) {
      return !getHasModality(sample, modality)
    }

    return true
  }

  // Get the current state of the tri-state checkbox
  const getHeaderState = (modality) => {
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
      SINGLE_CELL: project.modality_samples.SINGLE_CELL
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
  const toggleModalitySamples = (modality) => {
    setSelectedSamples((prevSelectedSamples) => {
      const currentSelectedSamples = prevSelectedSamples[modality]

      // Exclude multiplexed samples unless SINGLE_CELLEXPERIMENT
      const updatedFilteredSamples = !canAddMultiplexed
        ? filteredSamples.filter((s) => !s.has_multiplexed_data)
        : filteredSamples

      const modalitySampleIds = updatedFilteredSamples
        .filter((s) => s[`has_${modality.toLowerCase()}_data`])
        .map((s) => s.scpca_id)

      // Exclude toggling of already-added samples on the Browse page
      const alreadyAddedSampleIds = canAdd
        ? getMyDatasetProjectDataSamples(project)[modality] || []
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
  const toggleSampleModality = (sample, modality) => {
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
    dataset,
    canAddMultiplexed,
    canAdd,
    canRemove,
    readOnly,
    allSamples,
    setAllSamples,
    selectedSamples,
    setSelectedSamples,
    filteredSamples,
    setFilteredSamples,
    showBulkInfoText,
    showWarningMultiplexed,
    getHeaderState,
    getCheckBoxIsChecked,
    getCheckBoxIsDisabled,
    selectAllSingleCellSamples,
    selectModalitySamplesByIds,
    toggleSampleModality,
    toggleModalitySamples
  }
}
