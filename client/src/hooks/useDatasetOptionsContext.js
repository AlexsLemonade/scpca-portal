import { useContext, useEffect } from 'react'
import { DatasetOptionsContext } from 'contexts/DatasetOptionsContext'
import { optionsSortOrder } from 'config/downloadOptions'
import { arrayListSort } from 'helpers/arrayListSort'
import { filterWhere } from 'helpers/filterWhere'
import { pick } from 'helpers/pick'
import { uniqueArray } from 'helpers/uniqueArray'
import { uniqueValuesForKey } from 'helpers/uniqueValuesForKey'

export const useDatasetOptionsContext = () => {
  const {
    computedFiles,
    excludeMultiplexed,
    setExcludeMultiplexed,
    format,
    setFormat,
    formatOptions,
    setFormatOptions,
    modalityOptions,
    setModalityOptions,
    selectedModalities,
    setSelectedModalities,
    resource,
    includeBulkRnaSeq,
    setIncludeBulkRnaSeq,
    isBulkRnaSeqAvailable,
    setIsBulkRnaSeqAvailable,
    includesMerged,
    setIncludesMerged,
    isMergedObjectsAvailable,
    setIsMergedObjectsAvailable,
    isExcludeMultiplexedAvailable,
    setIsExcludeMultiplexedAvailable,
    isSpatialSelected,
    setIsSpatialSelected
  } = useContext(DatasetOptionsContext)

  const getResourceType = () =>
    resource?.downloadable_sample_count > 0 ? 'Project' : 'Sample'
  const resourceType = getResourceType()

  const availableSingleCellSamples =
    (resource.samples &&
      resource.samples.filter((sample) =>
        sample.computed_files.some((file) => file.modality === 'SINGLE_CELL')
      )) ||
    []

  const availableSpatialSamples =
    (resource.samples &&
      resource.samples.filter((sample) =>
        sample.computed_files.some((file) => file.modality === 'SPATIAL')
      )) ||
    []

  const sampleDifferenceForSpatial = Math.abs(
    availableSingleCellSamples.length - availableSpatialSamples.length
  )

  const getOptionsAndDefault = (optionName, files = computedFiles) =>
    arrayListSort(uniqueArray(pick(files, optionName)), optionsSortOrder)

  const getFilteredFiles = (files = computedFiles) =>
    filterWhere(files, {
      modality: selectedModalities,
      format
    })

  // Initialize all available modality options
  // Update it on computedFiles change
  useEffect(() => {
    const initialModalityOptions = getOptionsAndDefault('modality')
    setModalityOptions(initialModalityOptions)
  }, [computedFiles])

  // Initialize the format and available formatOptions based on modalityOptions and
  // Update them on selectedModalities change
  useEffect(() => {
    const modalitiesToUse =
      selectedModalities.length > 0 ? selectedModalities : modalityOptions

    if (modalitiesToUse) {
      const modalityMatchedFiles = filterWhere(computedFiles, {
        modality: modalitiesToUse
      })

      const newFormatOptions = getOptionsAndDefault(
        'format',
        modalityMatchedFiles
      )

      setFormatOptions(newFormatOptions)
      setFormat((prev) =>
        newFormatOptions.includes(prev) ? prev : formatOptions[0]
      )
    }
  }, [selectedModalities, modalityOptions])

  // Set the availavility of spatial data
  useEffect(() => {
    if (selectedModalities) {
      setIsSpatialSelected(
        selectedModalities.includes(optionsSortOrder[3]) &&
          selectedModalities.length > 1
      )
    }
  }, [selectedModalities])

  // Set the availability of Bulk RNA-seq, multiplexed, and merged object data
  useEffect(() => {
    setIsBulkRnaSeqAvailable(
      uniqueValuesForKey(getFilteredFiles(), 'has_bulk_rna_seq').filter(
        (k) => k
      ).length >= 1
    )
    setIsExcludeMultiplexedAvailable(
      uniqueValuesForKey(getFilteredFiles(), 'has_multiplexed_data').length > 1
    )
    setIsMergedObjectsAvailable(
      uniqueValuesForKey(getFilteredFiles(), 'includes_merged').length > 1
    )
  }, [format, selectedModalities])

  // Update excludeMultiplexed depending on user selection
  useEffect(() => {
    setExcludeMultiplexed(
      !isExcludeMultiplexedAvailable && format === optionsSortOrder[2]
    )
  }, [format, isExcludeMultiplexedAvailable])

  // Update includesMerged depending on user selection
  useEffect(() => {
    if (!isMergedObjectsAvailable) setIncludesMerged(false)
  }, [isMergedObjectsAvailable, selectedModalities])

  return {
    excludeMultiplexed,
    setExcludeMultiplexed,
    modalityOptions,
    format,
    setFormat,
    formatOptions,
    resource,
    resourceType,
    includeBulkRnaSeq,
    setIncludeBulkRnaSeq,
    includesMerged,
    setIncludesMerged,
    isBulkRnaSeqAvailable,
    isExcludeMultiplexedAvailable,
    isMergedObjectsAvailable,
    isSpatialSelected,
    sampleDifferenceForSpatial,
    selectedModalities,
    setSelectedModalities
  }
}
