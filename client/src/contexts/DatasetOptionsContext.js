import React, { createContext, useState, useEffect } from 'react'

export const DatasetOptionsContext = createContext({})

export const DatasetOptionsContextProvider = ({ resource, children }) => {
  const [format, setFormat] = useState(null)

  // Control Bulk RNA-seq data option
  const [includeBulkRnaSeq, setIncludeBulkRnaSeq] = useState(false) // Checkbox
  const [isBulkRnaSeqAvailable, setIsBulkRnaSeqAvailable] = useState(false)

  // Control merged object option
  const [includesMerged, setIncludesMerged] = useState(false) // Checkbox
  const [isMergedObjectsAvailable, setIsMergedObjectsAvailable] =
    useState(false)

  // Control multiplexed data option
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false) // Checkbox
  const [isExcludeMultiplexedAvailable, setIsExcludeMultiplexedAvailable] =
    useState(false)

  // User-selected modalities to be added to My Dataset
  const [selectedModalities, setSelectedModalities] = useState([])

  // Initial potential format and modality for Options
  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  // Computed Files used to derive available options.
  const [computedFiles, setComputedFiles] = useState([])

  // Only on mount or when resource / collection name change
  useEffect(() => {
    if (resource) {
      setComputedFiles(() => {
        return resource.computed_files.filter((f) => !f.metadata_only) // Exclude the metadata_only file
      })
    }
  }, [resource])

  return (
    <DatasetOptionsContext.Provider
      value={{
        computedFiles,
        setComputedFiles,
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
        excludeMultiplexed,
        setExcludeMultiplexed
      }}
    >
      {children}
    </DatasetOptionsContext.Provider>
  )
}
