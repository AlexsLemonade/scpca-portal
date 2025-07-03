import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'

export const useDatasetManager = () => useContext(DatasetManagerContext)
