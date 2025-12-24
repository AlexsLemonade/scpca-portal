import { useContext } from 'react'
import { CCDLDatasetContext } from 'contexts/CCDLDatasetContext'

export const useCCDLDataset = () => {
  const { datasets } = useContext(CCDLDatasetContext)
  return { datasets }
}

export default useCCDLDataset
