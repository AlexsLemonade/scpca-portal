import React, { createContext, useState } from 'react'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const MyDatasetContext = createContext({})

export const MyDatasetContextProvider = ({ children }) => {
  const [myDataset, setMyDataset] = useLocalStorage('myDataset', {})
  const [datasets, setDatasets] = useLocalStorage('datasets', []) // List of user-created dataset IDs for historical references
  const [email, setEmail] = useLocalStorage('dataset-email', null) // Email associated with myDataset
  const [errors, setErrors] = useState([]) //  TODO: Stores runtime error messages as strings (data structure TBD)

  return (
    <MyDatasetContext.Provider
      value={{
        myDataset,
        setMyDataset,
        datasets,
        setDatasets,
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
