import React, { createContext, useState } from 'react'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const MyDatasetContext = createContext({})

export const MyDatasetContextProvider = ({ children }) => {
  const [myDataset, setMyDataset] = useLocalStorage('dataset', {})
  const [prevMyDatasetFormat, setPrevMyDatasetFormat] = useLocalStorage(
    // Previously selected format for comparing format changes
    'dataset-prev-format',
    ''
  )
  // Current format selected via the dropwdown in modals, used to disable multiplexed samples for AnnData
  const [userFormat, setUserFormat] = useLocalStorage('user-format')
  const [datasets, setDatasets] = useLocalStorage('datasets', []) // List of user-created dataset IDs for historical references
  const [email, setEmail] = useLocalStorage('dataset-email', null) // Email associated with myDataset
  const [errors, setErrors] = useState([]) //  TODO: Stores runtime error messages as strings (data structure TBD)

  return (
    <MyDatasetContext.Provider
      value={{
        myDataset,
        setMyDataset,
        prevMyDatasetFormat,
        setPrevMyDatasetFormat,
        datasets,
        setDatasets,
        email,
        setEmail,
        errors,
        setErrors,
        userFormat,
        setUserFormat
      }}
    >
      {children}
    </MyDatasetContext.Provider>
  )
}
