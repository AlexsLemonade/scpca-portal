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

  const getIsSampleSelected = (sample, modality) =>
    selectedSamples[modality].includes(sample.scpca_id)

  const getIsSamlpleSelectable = (sample, modality) => {
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

  const getSelectedSampleIdsOnPage = (modality) => {
    const allSampleIdsOnPage = filteredSamples.map((s) => s.scpca_id)
    const selectedModalitySampleIds = selectedSamples[modality]

    return allSampleIdsOnPage.filter((id) =>
      selectedModalitySampleIds.includes(id)
    )
  }

  const getIsAllSelected = (modality) => {
    const selectedSampleIdsOnPage = getSelectedSampleIdsOnPage(modality)
    return selectedSampleIdsOnPage.length === filteredSamples.length
  }

  const getIsNoneSelected = (modality) => {
    const selectedSampleIdsOnPage = getSelectedSampleIdsOnPage(modality)
    return selectedSampleIdsOnPage.length === 0
  }

  const getIsSomeSelected = (modality) =>
    !getIsAllSelected(modality) && !getIsNoneSelected(modality)

  const selectAllSingleCellSamples = () => {
    setSelectedSamples((prevSelectedSamples) => ({
      ...prevSelectedSamples,
      SINGLE_CELL: project.modality_samples.SINGLE_CELL
    }))
  }

  const selectModalitySamplesByIds = (modality, sampleIds) => {
    const sampleIdsSet = new Set(sampleIds)
    const samplesToBeSelected = allSamples
      .filter((s) => sampleIdsSet.has(s.scpca_id))
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

      // Exclude samples already added to the dataset (on the Browse page)
      const alreadyAddedSampleIds = canAdd
        ? getMyDatasetProjectDataSamples(project)[modality] || []
        : []

      // Samples that can be toggled in the table
      const sampleIdsToToggle = differenceArray(
        modalitySampleIds,
        alreadyAddedSampleIds
      )

      const currentSelectedSet = new Set(currentSelectedSamples)
      const isAllOrSomeSelected = sampleIdsToToggle.some((id) =>
        currentSelectedSet.has(id)
      )

      if (isAllOrSomeSelected) {
        // Remove currently selected toggleable samples
        return {
          ...prevSelectedSamples,
          [modality]: differenceArray(currentSelectedSamples, sampleIdsToToggle)
        }
      }

      return {
        ...prevSelectedSamples,
        [modality]: uniqueArray(currentSelectedSamples, sampleIdsToToggle)
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
    getIsAllSelected,
    getIsSomeSelected,
    getIsSampleSelected,
    getIsSamlpleSelectable,
    selectAllSingleCellSamples,
    selectModalitySamplesByIds,
    toggleSampleModality,
    toggleModalitySamples
  }
}
