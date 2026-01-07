import React, { createContext, useState } from 'react'

export const ProjectSamplesTableContext = createContext({})

/**
 * This context supports two states (per modality) in react-table (there is no built-in support for two checkbox states).
 *
 * e.g., The provider may be used as follows:
 * <ProjectSamplesTableContextProvider
 *    project={project}
 *    samples={samples}
 *    canAdd>
 *   <ProjectSamplesTable />  // Wrap a table component
 * </ProjectSamplesTableContextProvider>
 */
export const ProjectSamplesTableContextProvider = ({
  project,
  samples,
  dataset,
  canAdd = false,
  canRemove = false,
  children
}) => {
  const [allSamples, setAllSamples] = useState([]) // Stores all samples available in the table
  const [filteredSamples, setFilteredSamples] = useState([]) // Stores only visible and filtered samples on the selected page
  const [selectedSamples, setSelectedSamples] = useState({
    // Stores selected samples IDs per modality from the table
    SINGLE_CELL: [],
    SPATIAL: []
  })

  return (
    <ProjectSamplesTableContext.Provider
      value={{
        project,
        samples,
        dataset,
        canAdd,
        canRemove,
        readOnly: !canAdd && !canRemove,
        allSamples,
        setAllSamples,
        selectedSamples,
        setSelectedSamples,
        filteredSamples,
        setFilteredSamples
      }}
    >
      {children}
    </ProjectSamplesTableContext.Provider>
  )
}
