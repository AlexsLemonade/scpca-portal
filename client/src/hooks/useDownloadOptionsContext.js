import { useContext, useEffect } from 'react'
import { DownloadOptionsContext } from 'contexts/DownloadOptionsContext'
import { optionsSortOrder } from 'config/downloadOptions'
import { arrayListSort } from 'helpers/arrayListSort'
import { filterWhere } from 'helpers/filterWhere'
import { pick } from 'helpers/pick'
import { uniqueArray } from 'helpers/uniqueArray'
import { objectContains } from 'helpers/objectContains'
import { uniqueValuesForKey } from 'helpers/uniqueValuesForKey'

export const useDownloadOptionsContext = () => {
  const {
    computedFile,
    setComputedFile,
    computedFiles,
    format,
    setFormat,
    formatOptions,
    setFormatOptions,
    modality,
    setModality,
    modalityOptions,
    setModalityOptions,
    resource,
    resourceAttribute,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed,
    userModality,
    setUserModality,
    userFormat,
    setUserFormat
  } = useContext(DownloadOptionsContext)

  const getOptionsAndDefault = (
    optionName,
    preference,
    files = computedFiles
  ) => {
    const allOptions = arrayListSort(
      uniqueArray(pick(files, optionName)),
      optionsSortOrder
    )
    const filteredAllOptions = allOptions.filter((o) => o) // Exclude the metadata_only file
    const defaultOption = filteredAllOptions.includes(preference)
      ? preference
      : filteredAllOptions[0]
    return [allOptions, defaultOption]
  }

  const getFilteredFiles = (files = computedFiles) =>
    filterWhere(files, { modality, format })

  // Get the first computed file that matches modality and format
  const getFoundFile = (
    files = computedFiles,
    ignoreAdditionalOptions = false
  ) => {
    const filterObject = { modality, format }
    // when checking has_multiplexed_data we wither want both or just true
    if (!ignoreAdditionalOptions) {
      filterObject.includes_merged = includesMerged
      filterObject.has_multiplexed_data = !excludeMultiplexed
    }
    return files.find((file) => objectContains(file, filterObject))
  }

  // Check the availability of the merged objects
  const isMergedObjectsAvailable =
    uniqueValuesForKey(getFilteredFiles(), 'includes_merged').length > 1

  // Check availability of multiplexed data
  const isExcludeMultiplexedAvailable =
    uniqueValuesForKey(getFilteredFiles(), 'has_multiplexed_data').length > 1

  // Sorter function for ordering a resource
  // based on availability of prefered download options
  const resourceSort = (
    { computed_files: firstFiles },
    { computed_files: secondFiles }
  ) => {
    const firstFiltered = getFilteredFiles(firstFiles)
    const secondFiltered = getFilteredFiles(secondFiles)
    return firstFiltered.length < secondFiltered.length
  }

  // Save user preferences
  // Can be specified, but defaults to what is currently set
  const saveUserPreferences = (newModality = modality, newFormat = format) => {
    setUserModality(newModality)
    setUserFormat(newFormat)
  }

  // When computed files change, update modality to ensure it is possible
  // Initialize the context when computed files change
  useEffect(() => {
    const [newModalityOptions, newModality] = getOptionsAndDefault(
      'modality',
      userModality
    )
    setModalityOptions(newModalityOptions)
    setModality(newModality)
  }, [computedFiles])

  // Update available data format when the user-selected modality changes
  useEffect(() => {
    if (modality) {
      const modalityMatchedFiles = filterWhere(computedFiles, {
        modality
      })
      const [newFormatOptions, newFormat] = getOptionsAndDefault(
        'format',
        userFormat,
        modalityMatchedFiles
      )
      setFormatOptions(newFormatOptions)
      // Only assign format when unset
      setFormat(newFormat)
    }
  }, [modality])

  // Update computed file when download options resolves to a computed file
  // This only needs to be updated when the user is configuring the passed in resource.
  // Otherwise you can call useDownloadOptionsContext.getFoundFile directy ex. samples table
  useEffect(() => {
    if (!resourceAttribute) {
      const newComputedFile = getFoundFile()
      if (newComputedFile) setComputedFile(newComputedFile)
    }
  }, [modality, format, includesMerged, excludeMultiplexed])

  // Update excludeMultiplexed depending on availability.
  useEffect(() => {
    setExcludeMultiplexed(!isExcludeMultiplexedAvailable)
  }, [isExcludeMultiplexedAvailable])

  // Update includesMerged depending on availability.
  useEffect(() => {
    if (!isMergedObjectsAvailable) setIncludesMerged(false)
  }, [isMergedObjectsAvailable])

  return {
    modality,
    setModality,
    modalityOptions,
    format,
    setFormat,
    formatOptions,
    computedFile,
    computedFiles,
    getFoundFile,
    isMergedObjectsAvailable,
    isExcludeMultiplexedAvailable,
    getOptionsAndDefault,
    saveUserPreferences,
    resourceSort,
    resource,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed
  }
}
