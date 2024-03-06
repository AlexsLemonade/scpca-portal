import { useContext, useEffect } from 'react'
import { DownloadOptionsContext } from 'contexts/DownloadOptionsContext'
import pick from 'helpers/pick'
import filterWhere from 'helpers/filterWhere'
import { optionsSortOrder } from 'config/downloadOptions'
import arrayListSort from 'helpers/arrayListSort'

export const useDownloadOptionsContext = (autoApply = false) => {
  // Shared Context
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
    getSelectedFilteredFiles,
    setModalityOptions,
    setFormatOptions,
    computedFiles,
    selectedModality,
    setComputedFile,
    setSelectedFormat,
    setSelectedModality,
    selectedFormat,
    resourceAttribute
  } = useContext(DownloadOptionsContext)

  // If the direct consumer of this hook
  // wants to update download options when selections change.
  useEffect(() => {
    if (autoApply) applySelection()
  }, [selectedModality, selectedFormat])

  // When computed files change, update modality to ensure it is possible
  // Initialize the context when computed files change
  useEffect(() => {
    const [newModality, newModalityOptions] = getOptionsAndDefault(
      'modality',
      userModality
    )
    setModalityOptions(newModalityOptions)
    setSelectedModality(newModality)
    setModality(newModality)
  }, [computedFiles])

  // Update format when modality changes to ensure that it is possible
  useEffect(() => {
    if (selectedModality) {
      const modalityMatchedFiles = filterWhere(computedFiles, {
        modality: selectedModality
      })
      const [newFormat, newFormatOptions] = getOptionsAndDefault(
        'format',
        userFormat,
        modalityMatchedFiles
      )
      setFormatOptions(newFormatOptions)
      setSelectedFormat(newFormat)
      // Only assign format when unset
      if (!format) setFormat(newFormat)
    }
  }, [selectedModality])

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
    return [defaultOption, allOptions]
  }

  const getFilteredFiles = (files = computedFiles) =>
    filterWhere(files, { modality, format })

  // Get the first computed file that matches modality and format
  const getFoundFile = (files = computedFiles) =>
    files.find((file) => file.modality === modality && file.format === format)

  // Sort resources by how compatible they are with download settings
  const resourceSort = (
    { computed_files: firstFiles },
    { computed_files: secondFiles }
  ) => {
    const firstFiltered = getFilteredFiles(firstFiles)
    const secondFiltered = getFilteredFiles(secondFiles)
    return firstFiltered.length < secondFiltered.length
  }

  // Apply current selection to
  const applySelection = () => {
    // Set Context Settings
    setModality(selectedModality)
    setFormat(selectedFormat)

    // Set user preferences
    setUserModality(selectedModality)
    setUserFormat(selectedFormat)
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
    selectedModality,
    setSelectedModality,
    selectedFormat,
    setSelectedFormat,
    applySelection,
    getSelectedFilteredFiles,
    resourceSort,
    resource
  }
}
