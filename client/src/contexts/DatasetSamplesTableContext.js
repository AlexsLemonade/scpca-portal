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
  const [allSamples, setAllSamples] = useState([]) // Stores all samples available in the table
  const [filteredSamples, setFilteredSamples] = useState([]) // Stores only visible and filtered samples on the selected page
  const [selectedSamples, setSelectedSamples] = useState({
    // Stores selected samples IDs per modality from the table
    SINGLE_CELL: [],
    SPATIAL: []
  })

  return (
    <DatasetSamplesTableContext.Provider
      value={{
        allSamples,
        setAllSamples,
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
