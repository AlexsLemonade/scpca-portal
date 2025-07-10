import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { useScPCAPortal } from './useScPCAPortal'

export const useDatasetManager = () => {
  const { myDataset, setMyDataset, datasets, setDatasets, email, setEmail } =
    useContext(DatasetManagerContext)
  const { userFormat, setUserFormat } = useScPCAPortal()

  return {
    myDataset,
    setMyDataset, // Temporary
    datasets,
    setDatasets, // Temporary
    email,
    setEmail, // Temporary
    userFormat,
    setUserFormat // Temporary
  }
}
