import React, { createContext, useState } from 'react'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const MyDatasetContext = createContext({})

export const MyDatasetContextProvider = ({ children }) => {
  const [myDataset, setMyDataset] = useLocalStorage('dataset', {})
  const [datasets, setDatasets] = useLocalStorage('datasets', []) // List of user-created dataset IDs for historical references
  const [email, setEmail] = useLocalStorage('dataset-email', null) // Email associated with myDataset
  const [errors, setErrors] = useState([]) //  TODO: Stores runtime error messages as strings (data structure TBD)
  // The most recent user-selected project options for myDataset
  const [datasetProjectOptions, setDatasetProjectOptions] = useLocalStorage(
    'dataset-project-options',
    {
      includeBulk: false,
      includeMerge: false,
      modalities: []
    }
  )

  return (
    <MyDatasetContext.Provider
      value={{
        myDataset,
        setMyDataset,
        datasets,
        setDatasets,
        datasetProjectOptions,
        setDatasetProjectOptions,
        email,
        setEmail,
        errors,
        setErrors
      }}
    >
      {children}
    </MyDatasetContext.Provider>
  )
}
