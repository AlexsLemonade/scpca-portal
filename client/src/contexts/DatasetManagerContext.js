import React, { createContext, useContext } from 'react'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const DatasetManagerContext = createContext({})

export const DatasetManagerContextProvider = ({ children }) => {
  const { userFormat, setUserFormat } = useContext(ScPCAPortalContext)

  const [myDataset, setMyDataset] = useLocalStorage({})
  const [datasets, setDatasets] = useLocalStorage([]) // List of user-created dataset IDs for historical references
  const [email, setEmail] = useLocalStorage(null) // Email associated with myDataset

  return (
    <DatasetManagerContext.Provider
      value={{
        myDataset,
        setMyDataset,
        datasets,
        setDatasets,
        email,
        setEmail,
        userFormat,
        setUserFormat
      }}
    >
      {children}
    </DatasetManagerContext.Provider>
  )
}
