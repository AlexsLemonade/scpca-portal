import { useContext, useEffect } from 'react'
import { DownloadOptionsContext } from 'contexts/DownloadOptionsContext'
import pick from 'helpers/pick'
import filterWhere from 'helpers/filterWhere'
import { mergedObjectsKeys, optionsSortOrder } from 'config/downloadOptions'
import arrayListSort from 'helpers/arrayListSort'

export const useDownloadOptionsContext = () => {
  const {
    resource,
    userModality,
    setUserModality,
    userFormat,
    setUserFormat,
    modality,
    setModality,
    format,
    setFormat,
    modalityOptions,
    formatOptions,
    computedFile,
    setModalityOptions,
    setFormatOptions,
    computedFiles,
    setComputedFile,
    resourceAttribute
  } = useContext(DownloadOptionsContext)

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

  // Update format when modality changes to ensure that it is possible
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
  }, [modality, format])

  const getOptionsAndDefault = (
    optionName,
    preference,
    files = computedFiles
  ) => {
    const allOptions = arrayListSort(
      [...new Set(pick(files, optionName))],
      optionsSortOrder
    )
    const defaultOption = allOptions.includes(preference)
      ? preference
      : allOptions[0]
    return [allOptions, defaultOption]
  }

  const getFilteredFiles = (files = computedFiles) =>
    filterWhere(files, { modality, format })

  // Get the first computed file that matches modality and format
  const getFoundFile = (files = computedFiles) =>
    files.find((file) => file.modality === modality && file.format === format)

  // Check the availability of the merged objects download based on modalities and 'includes_merged' flag per computed file
  const isMergedObjectsAvailable =
    mergedObjectsKeys.includes(modality) &&
    computedFiles.some((cf) => cf.includes_merged)

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

  return {
    modality,
    setModality,
    modalityOptions,
    format,
    setFormat,
    formatOptions,
    computedFile,
    getFoundFile,
    isMergedObjectsAvailable,
    saveUserPreferences,
    resourceSort,
    resource
  }
}
