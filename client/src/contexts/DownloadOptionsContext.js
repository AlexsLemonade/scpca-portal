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
  const [includesMerged, setIncludesMerged] = useState(false)
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)

  // Potential Values for Download Options
  const [modalityOptions, setModalityOptions] = useState([])
  const [formatOptions, setFormatOptions] = useState([])

  // Computed Files used to derive available options.
  const [computedFiles, setComputedFiles] = useState([])

  // Automatically updated computed file for resource
  // This does *not* work when attribute specified.
  const [computedFile, setComputedFile] = useState(null)

  // Only on mount or when resource / collection name change
  useEffect(() => {
    if (resource) {
      setComputedFiles(() => {
        if (!resourceAttribute) return resource.computed_files
        return pick(resource[resourceAttribute], 'computed_files').flat()
      })
    }
  }, [resource, resourceAttribute])

  return (
    <DownloadOptionsContext.Provider
      value={{
        computedFile,
        setComputedFile,
        computedFiles,
        setComputedFiles,
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
      }}
    >
      {children}
    </DownloadOptionsContext.Provider>
  )
}
