import React, { createContext, useEffect, useState } from 'react'
import { api } from 'api'

export const CCDLDatasetContext = createContext({})

export const CCDLDatasetContextProvider = ({ initialQuery = {}, children }) => {
  const [query, setQuery] = useState(initialQuery)
  const [datasets, setDatasets] = useState([])
  // TODO: instead of loading immediately we should have an option to defer this

  // Set states for the portal metadata
  useEffect(() => {
    const getCCDLDatasets = async () => {
      const resourceRequest = await api.ccdlDatasets.list(query)
      const { results } = resourceRequest.response
      setDatasets(results)
    }

    getCCDLDatasets()
  }, [query])

  return (
    <CCDLDatasetContext.Provider
      value={{ query, setQuery, datasets, setDatasets }}
    >
      {children}
    </CCDLDatasetContext.Provider>
  )
}
