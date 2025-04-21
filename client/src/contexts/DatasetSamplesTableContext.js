import React, { createContext, useState } from 'react'

export const DatasetSamplesTableContext = createContext({})

/**
 * NOTE: This context supports two states (per modality) in react-table (there is no built-in support for two checkbox states).
 * Implementation details are subject to change based on the data structure returned via API.
 * Temporarily using the sample endpoint's response and replacing 'computed_files' with the 'data' object to mimic the dataset.
 *
 * e.g., The provider may be used as follows:
 * <DatasetSamplesTableContextProvider>
 *   <DatasetSamplesTable />  // Wrap a table component
 * </DatasetSamplesTableContextProvider>
 */
export const DatasetSamplesTableContextProvider = ({ children }) => {
  const [selectedSamples, setSelectedSamples] = useState({
    // user-selected samples IDs per modality from the table (could store entire samples objects etc)
    SINGLE_CELL: [],
    SPATIAL: []
  })

  const [filteredSamples, setFilteredSamples] = useState([]) // stores only visible and filtered samples on the selected page

  return (
    <DatasetSamplesTableContext.Provider
      value={{
        selectedSamples,
        setSelectedSamples,
        filteredSamples,
        setFilteredSamples
      }}
    >
      {children}
    </DatasetSamplesTableContext.Provider>
  )
}
