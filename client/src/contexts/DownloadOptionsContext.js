import React, { createContext, useState, useEffect, useContext } from 'react'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import pick from 'helpers/pick'

export const DownloadOptionsContext = createContext({})

export const DownloadOptionsContextProvider = ({
  resource,
  attribute: resourceAttribute = '',
  children
}) => {
  // Save users last used as preference.
  const { userModality, setUserModality, userFormat, setUserFormat } =
    useContext(ScPCAPortalContext)

  // Download Options
  const [modality, setModality] = useState(null)
  const [format, setFormat] = useState(null)
  const [selectedMerged, setSelectedMerged] = useState(false)

  // Potential Values for Download Options
  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  // Computed Files used to derive available options.
  const [computedFiles, setComputeFiles] = useState([])

  // Automatically updated computed file for resource
  // This does *not* work when attribute specified.
  const [computedFile, setComputedFile] = useState(null)

  // Only on mount or when resource / collection name change
  useEffect(() => {
    if (resource) {
      setComputeFiles(() => {
        if (!resourceAttribute) return resource.computed_files
        return pick(resource[resourceAttribute], 'computed_files').flat()
      })
    }
  }, [resource, resourceAttribute])

  return (
    <DownloadOptionsContext.Provider
      value={{
        computedFile,
        computedFiles,
        setComputedFile,
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
        selectedMerged,
        setSelectedMerged,
        userModality,
        setUserModality,
        userFormat,
        setUserFormat
      }}
    >
      {children}
    </DownloadOptionsContext.Provider>
  )
}