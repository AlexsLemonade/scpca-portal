import React, { createContext, useState, useEffect } from 'react'
import { api } from 'api'

export const DatasetOptionsContext = createContext({})

export const DatasetOptionsContextProvider = ({
  resource: initialResource,
  children
}) => {
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

  // Control spatial data option
  const [isSpatialSelected, setIsSpatialSelected] = useState(false)

  // User-selected modalities to be added to My Dataset
  const [selectedModalities, setSelectedModalities] = useState([])

  // Initial potential format and modality options
  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  // Computed Files used to derive available options.
  const [computedFiles, setComputedFiles] = useState([])
  // Store the updated initialResource for the project browse page
  const [resource, setResource] = useState({})

  // Only on mount or when resource / collection name change
  useEffect(() => {
    const fetchSamplesDetails = async (projectId) => {
      const response = await api.projects.get(projectId)
      return response
    }

    const updateSamples = async () => {
      if (initialResource) {
        if (typeof initialResource.samples[0] === 'string') {
          const response = await fetchSamplesDetails(initialResource.scpca_id)
          setResource({
            ...initialResource,
            samples: response.response.samples
          })
        } else {
          setResource(initialResource)
        }
      }
    }

    if (initialResource) {
      updateSamples() // Fetch and update the samples to be an array of objects
      setComputedFiles(() => {
        return initialResource.computed_files.filter((f) => !f.metadata_only) // Exclude the metadata_only file
      })
    }
  }, [initialResource])

  return (
    <DatasetOptionsContext.Provider
      value={{
        computedFiles,
        setComputedFiles,
        format,
        excludeMultiplexed,
        setExcludeMultiplexed,
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
      }}
    >
      {children}
    </DatasetOptionsContext.Provider>
  )
}
